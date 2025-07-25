from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import csv
import io
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(200))
    is_profile_public = db.Column(db.Boolean, default=True)
    fitness_goal = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    workouts = db.relationship('Workout', backref='user', lazy=True, cascade='all, delete-orphan')
    bmi_records = db.relationship('BMIRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # Friend relationships
    sent_requests = db.relationship('FriendRequest', foreign_keys='FriendRequest.sender_id', backref='sender', lazy='dynamic')
    received_requests = db.relationship('FriendRequest', foreign_keys='FriendRequest.receiver_id', backref='receiver', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def get_friends(self):
        """Get all confirmed friends"""
        friend_requests = db.session.query(FriendRequest).filter(
            ((FriendRequest.sender_id == self.id) | (FriendRequest.receiver_id == self.id)) &
            (FriendRequest.status == 'accepted')
        ).all()
        
        friends = []
        for request in friend_requests:
            if request.sender_id == self.id:
                friends.append(request.receiver)
            else:
                friends.append(request.sender)
        return friends
    
    def is_friend_with(self, user):
        """Check if this user is friends with another user"""
        return db.session.query(FriendRequest).filter(
            ((FriendRequest.sender_id == self.id) & (FriendRequest.receiver_id == user.id)) |
            ((FriendRequest.sender_id == user.id) & (FriendRequest.receiver_id == self.id))
        ).filter(FriendRequest.status == 'accepted').first() is not None

class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'declined'
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WorkoutShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    shared_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    caption = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)  # Public feed or friends only
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    workout = db.relationship('Workout', backref='shares')
    sharer = db.relationship('User', backref='shared_workouts')
    likes = db.relationship('WorkoutLike', backref='shared_workout', cascade='all, delete-orphan')
    comments = db.relationship('WorkoutComment', backref='shared_workout', cascade='all, delete-orphan')

class WorkoutLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workout_share_id = db.Column(db.Integer, db.ForeignKey('workout_share.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='workout_likes')

class WorkoutComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workout_share_id = db.Column(db.Integer, db.ForeignKey('workout_share.id'), nullable=False)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='workout_comments')

class FitnessGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    target_value = db.Column(db.Float)
    current_value = db.Column(db.Float, default=0)
    unit = db.Column(db.String(20))  # 'lbs', 'kg', 'miles', 'minutes', etc.
    goal_type = db.Column(db.String(50))  # 'weight_loss', 'muscle_gain', 'endurance', 'strength'
    target_date = db.Column(db.Date)
    is_public = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'paused'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='fitness_goals')

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    muscle_group = db.Column(db.String(50))
    description = db.Column(db.Text)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_name = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer)  # in minutes
    calories_burned = db.Column(db.Float)
    weight = db.Column(db.Float)  # weight used
    
    # Walking/Cardio specific fields
    speed = db.Column(db.Float)  # in mph or km/h
    incline = db.Column(db.Float)  # in percentage or degrees
    distance = db.Column(db.Float)  # in miles or km
    avg_heart_rate = db.Column(db.Integer)  # beats per minute
    workout_type = db.Column(db.String(20), default='strength')  # 'strength', 'cardio', 'walking'
    
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BMIRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    height = db.Column(db.Float, nullable=False)  # in cm
    weight = db.Column(db.Float, nullable=False)  # in kg
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # 'male', 'female'
    activity_level = db.Column(db.String(20), nullable=False)  # 'sedentary', 'light', 'moderate', 'active', 'very_active'
    body_type = db.Column(db.String(20))  # 'ectomorph', 'mesomorph', 'endomorph'
    
    # Calculated values
    bmi = db.Column(db.Float)
    bmi_category = db.Column(db.String(20))
    body_fat_percentage = db.Column(db.Float)
    skeletal_muscle_mass = db.Column(db.Float)  # in kg
    lean_body_mass = db.Column(db.Float)  # in kg
    ideal_weight = db.Column(db.Float)  # in kg
    bmr = db.Column(db.Float)  # Basal Metabolic Rate
    tdee = db.Column(db.Float)  # Total Daily Energy Expenditure
    
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_bmi(self):
        """Calculate BMI from height and weight"""
        height_m = self.height / 100  # convert cm to meters
        self.bmi = round(self.weight / (height_m ** 2), 1)
        
        # Determine BMI category
        if self.bmi < 18.5:
            self.bmi_category = 'Underweight'
        elif self.bmi < 25:
            self.bmi_category = 'Normal weight'
        elif self.bmi < 30:
            self.bmi_category = 'Overweight'
        else:
            self.bmi_category = 'Obese'
    
    def calculate_body_fat_percentage(self):
        """Calculate body fat percentage using Navy method approximation"""
        if self.gender == 'male':
            # Simplified male body fat estimation
            self.body_fat_percentage = round((1.20 * self.bmi) + (0.23 * self.age) - 16.2, 1)
        else:
            # Simplified female body fat estimation  
            self.body_fat_percentage = round((1.20 * self.bmi) + (0.23 * self.age) - 5.4, 1)
        
        # Ensure reasonable bounds
        self.body_fat_percentage = max(3, min(50, self.body_fat_percentage))
    
    def calculate_lean_mass_and_muscle(self):
        """Calculate lean body mass and skeletal muscle mass"""
        fat_mass = (self.body_fat_percentage / 100) * self.weight
        self.lean_body_mass = round(self.weight - fat_mass, 1)
        
        # Skeletal muscle mass is approximately 40-45% of lean body mass
        muscle_percentage = 0.45 if self.gender == 'male' else 0.40
        self.skeletal_muscle_mass = round(self.lean_body_mass * muscle_percentage, 1)
    
    def calculate_bmr(self):
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation"""
        if self.gender == 'male':
            self.bmr = round((10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 5)
        else:
            self.bmr = round((10 * self.weight) + (6.25 * self.height) - (5 * self.age) - 161)
    
    def calculate_tdee(self):
        """Calculate Total Daily Energy Expenditure"""
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        multiplier = activity_multipliers.get(self.activity_level, 1.2)
        self.tdee = round(self.bmr * multiplier)
    
    def calculate_ideal_weight(self):
        """Calculate ideal weight using Devine formula"""
        if self.gender == 'male':
            # For men: 50 kg + 2.3 kg per inch over 5 feet
            height_inches = self.height / 2.54
            if height_inches > 60:
                self.ideal_weight = round(50 + (2.3 * (height_inches - 60)), 1)
            else:
                self.ideal_weight = round(50 - (2.3 * (60 - height_inches)), 1)
        else:
            # For women: 45.5 kg + 2.3 kg per inch over 5 feet
            height_inches = self.height / 2.54
            if height_inches > 60:
                self.ideal_weight = round(45.5 + (2.3 * (height_inches - 60)), 1)
            else:
                self.ideal_weight = round(45.5 - (2.3 * (60 - height_inches)), 1)
    
    def perform_all_calculations(self):
        """Perform all body composition calculations"""
        self.calculate_bmi()
        self.calculate_body_fat_percentage()
        self.calculate_lean_mass_and_muscle()
        self.calculate_bmr()
        self.calculate_tdee()
        self.calculate_ideal_weight()

# Session-based auth decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    
    # Get recent workouts
    recent_workouts = Workout.query.filter_by(user_id=user_id).order_by(Workout.date.desc()).limit(5).all()
    
    # Get weekly stats
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_workouts = Workout.query.filter(
        Workout.user_id == user_id,
        Workout.date >= week_ago
    ).all()
    
    weekly_stats = {
        'total_workouts': len(weekly_workouts),
        'total_calories': sum(w.calories_burned or 0 for w in weekly_workouts),
        'total_duration': sum(w.duration or 0 for w in weekly_workouts),
        'total_sets': sum(w.sets or 0 for w in weekly_workouts)
    }
    
    # Get workout distribution by day
    daily_workouts = {}
    for workout in weekly_workouts:
        day = workout.date.strftime('%A')
        daily_workouts[day] = daily_workouts.get(day, 0) + 1
    
    return render_template('dashboard.html', 
                         recent_workouts=recent_workouts,
                         weekly_stats=weekly_stats,
                         daily_workouts=daily_workouts)

@app.route('/workouts')
@login_required
def workouts():
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    workouts = Workout.query.filter_by(user_id=user_id).order_by(Workout.date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('workouts.html', workouts=workouts)

@app.route('/add_workout', methods=['GET', 'POST'])
@login_required
def add_workout():
    if request.method == 'POST':
        workout = Workout(
            user_id=session['user_id'],
            exercise_name=request.form['exercise_name'],
            sets=int(request.form['sets']) if request.form.get('sets') else 1,
            reps=int(request.form['reps']) if request.form.get('reps') else 1,
            duration=int(request.form['duration']) if request.form['duration'] else None,
            calories_burned=float(request.form['calories_burned']) if request.form['calories_burned'] else None,
            weight=float(request.form['weight']) if request.form['weight'] else None,
            
            # Walking/Cardio fields
            speed=float(request.form['speed']) if request.form.get('speed') else None,
            incline=float(request.form['incline']) if request.form.get('incline') else None,
            distance=float(request.form['distance']) if request.form.get('distance') else None,
            avg_heart_rate=int(request.form['avg_heart_rate']) if request.form.get('avg_heart_rate') else None,
            workout_type=request.form.get('workout_type', 'strength'),
            
            notes=request.form['notes'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d') if request.form['date'] else datetime.utcnow()
        )
        
        db.session.add(workout)
        db.session.commit()
        flash('Workout added successfully!', 'success')
        return redirect(url_for('workouts'))
    
    return render_template('add_workout.html', datetime=datetime)

@app.route('/edit_workout/<int:workout_id>', methods=['GET', 'POST'])
@login_required
def edit_workout(workout_id):
    workout = Workout.query.filter_by(id=workout_id, user_id=session['user_id']).first_or_404()
    
    if request.method == 'POST':
        workout.exercise_name = request.form['exercise_name']
        workout.sets = int(request.form['sets']) if request.form.get('sets') else 1
        workout.reps = int(request.form['reps']) if request.form.get('reps') else 1
        workout.duration = int(request.form['duration']) if request.form['duration'] else None
        workout.calories_burned = float(request.form['calories_burned']) if request.form['calories_burned'] else None
        workout.weight = float(request.form['weight']) if request.form['weight'] else None
        
        # Walking/Cardio fields
        workout.speed = float(request.form['speed']) if request.form.get('speed') else None
        workout.incline = float(request.form['incline']) if request.form.get('incline') else None
        workout.distance = float(request.form['distance']) if request.form.get('distance') else None
        workout.avg_heart_rate = int(request.form['avg_heart_rate']) if request.form.get('avg_heart_rate') else None
        workout.workout_type = request.form.get('workout_type', 'strength')
        
        workout.notes = request.form['notes']
        workout.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        
        db.session.commit()
        flash('Workout updated successfully!', 'success')
        return redirect(url_for('workouts'))
    
    return render_template('edit_workout.html', workout=workout)

@app.route('/delete_workout/<int:workout_id>', methods=['POST'])
@login_required
def delete_workout(workout_id):
    workout = Workout.query.filter_by(id=workout_id, user_id=session['user_id']).first_or_404()
    db.session.delete(workout)
    db.session.commit()
    flash('Workout deleted successfully!', 'success')
    return redirect(url_for('workouts'))

@app.route('/export_csv')
@login_required
def export_csv():
    user_id = session['user_id']
    workouts = Workout.query.filter_by(user_id=user_id).order_by(Workout.date.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Exercise', 'Type', 'Sets', 'Reps', 'Duration (min)', 'Calories Burned', 
                    'Weight (kg)', 'Speed (mph)', 'Incline (%)', 'Distance (mi)', 'Avg Heart Rate', 'Notes'])
    
    # Write data
    for workout in workouts:
        writer.writerow([
            workout.date.strftime('%Y-%m-%d %H:%M'),
            workout.exercise_name,
            workout.workout_type or 'strength',
            workout.sets,
            workout.reps,
            workout.duration or '',
            workout.calories_burned or '',
            workout.weight or '',
            workout.speed or '',
            workout.incline or '',
            workout.distance or '',
            workout.avg_heart_rate or '',
            workout.notes or ''
        ])
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=fitness_data_{datetime.now().strftime("%Y%m%d")}.csv'
    
    return response

# API Routes for AJAX
@app.route('/api/workout_stats')
@login_required
def api_workout_stats():
    user_id = session['user_id']
    days = request.args.get('days', 30, type=int)
    
    start_date = datetime.utcnow() - timedelta(days=days)
    workouts = Workout.query.filter(
        Workout.user_id == user_id,
        Workout.date >= start_date
    ).all()
    
    # Group by date
    daily_stats = {}
    for workout in workouts:
        date_str = workout.date.strftime('%Y-%m-%d')
        if date_str not in daily_stats:
            daily_stats[date_str] = {
                'workouts': 0,
                'calories': 0,
                'duration': 0
            }
        daily_stats[date_str]['workouts'] += 1
        daily_stats[date_str]['calories'] += workout.calories_burned or 0
        daily_stats[date_str]['duration'] += workout.duration or 0
    
    return jsonify(daily_stats)

# BMI and Body Composition Routes
@app.route('/bmi')
@login_required
def bmi_tracker():
    user_id = session['user_id']
    
    # Get latest BMI record
    latest_bmi = BMIRecord.query.filter_by(user_id=user_id).order_by(BMIRecord.date_recorded.desc()).first()
    
    # Get BMI history for charts
    bmi_history = BMIRecord.query.filter_by(user_id=user_id).order_by(BMIRecord.date_recorded.desc()).limit(10).all()
    
    return render_template('bmi_tracker.html', latest_bmi=latest_bmi, bmi_history=bmi_history)

@app.route('/add_bmi', methods=['GET', 'POST'])
@login_required
def add_bmi():
    if request.method == 'POST':
        user_id = session['user_id']
        
        # Create new BMI record
        bmi_record = BMIRecord(
            user_id=user_id,
            height=float(request.form['height']),
            weight=float(request.form['weight']),
            age=int(request.form['age']),
            gender=request.form['gender'],
            activity_level=request.form['activity_level'],
            body_type=request.form.get('body_type'),
        )
        
        # Perform all calculations
        bmi_record.perform_all_calculations()
        
        db.session.add(bmi_record)
        db.session.commit()
        
        flash('Body composition analysis added successfully!', 'success')
        return redirect(url_for('bmi_tracker'))
    
    return render_template('add_bmi.html')

@app.route('/bmi_history')
@login_required
def bmi_history():
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    bmi_records = BMIRecord.query.filter_by(user_id=user_id).order_by(BMIRecord.date_recorded.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('bmi_history.html', bmi_records=bmi_records)

@app.route('/edit_bmi/<int:bmi_id>', methods=['GET', 'POST'])
@login_required
def edit_bmi(bmi_id):
    bmi_record = BMIRecord.query.filter_by(id=bmi_id, user_id=session['user_id']).first_or_404()
    
    if request.method == 'POST':
        bmi_record.height = float(request.form['height'])
        bmi_record.weight = float(request.form['weight'])
        bmi_record.age = int(request.form['age'])
        bmi_record.gender = request.form['gender']
        bmi_record.activity_level = request.form['activity_level']
        bmi_record.body_type = request.form.get('body_type')
        
        # Recalculate all values
        bmi_record.perform_all_calculations()
        
        db.session.commit()
        flash('Body composition analysis updated successfully!', 'success')
        return redirect(url_for('bmi_tracker'))
    
    return render_template('edit_bmi.html', bmi_record=bmi_record)

@app.route('/delete_bmi/<int:bmi_id>', methods=['POST'])
@login_required
def delete_bmi(bmi_id):
    bmi_record = BMIRecord.query.filter_by(id=bmi_id, user_id=session['user_id']).first_or_404()
    db.session.delete(bmi_record)
    db.session.commit()
    flash('BMI record deleted successfully!', 'success')
    return redirect(url_for('bmi_history'))

@app.route('/api/bmi_stats')
@login_required
def api_bmi_stats():
    user_id = session['user_id']
    
    bmi_records = BMIRecord.query.filter_by(user_id=user_id).order_by(BMIRecord.date_recorded.asc()).all()
    
    # Prepare data for charts
    chart_data = {
        'dates': [record.date_recorded.strftime('%Y-%m-%d') for record in bmi_records],
        'weight': [record.weight for record in bmi_records],
        'bmi': [record.bmi for record in bmi_records],
        'body_fat': [record.body_fat_percentage for record in bmi_records],
        'muscle_mass': [record.skeletal_muscle_mass for record in bmi_records]
    }
    
    return jsonify(chart_data)

def init_db():
    """Initialize the database with sample data"""
    db.create_all()
    
    # Add sample exercises if none exist
    if not Exercise.query.first():
        sample_exercises = [
            Exercise(name='Push-ups', category='Strength', muscle_group='Chest', description='Classic bodyweight exercise'),
            Exercise(name='Squats', category='Strength', muscle_group='Legs', description='Lower body compound movement'),
            Exercise(name='Running', category='Cardio', muscle_group='Full Body', description='Cardiovascular exercise'),
            Exercise(name='Pull-ups', category='Strength', muscle_group='Back', description='Upper body pulling exercise'),
            Exercise(name='Plank', category='Core', muscle_group='Core', description='Isometric core exercise'),
            Exercise(name='Deadlift', category='Strength', muscle_group='Full Body', description='Compound strength exercise'),
            Exercise(name='Burpees', category='HIIT', muscle_group='Full Body', description='High-intensity exercise'),
            Exercise(name='Cycling', category='Cardio', muscle_group='Legs', description='Low-impact cardio'),
        ]
        
        for exercise in sample_exercises:
            db.session.add(exercise)
        db.session.commit()

# Social Features Routes
@app.route('/social')
@login_required
def social_feed():
    user_id = session['user_id']
    current_user = User.query.get(user_id)
    
    # Get friends' shared workouts and public posts
    friends = current_user.get_friends()
    friend_ids = [friend.id for friend in friends]
    friend_ids.append(user_id)  # Include own posts
    
    # Get shared workouts from friends and public posts
    shared_workouts = WorkoutShare.query.filter(
        (WorkoutShare.shared_by.in_(friend_ids)) | 
        (WorkoutShare.is_public == True)
    ).order_by(WorkoutShare.created_at.desc()).limit(20).all()
    
    # Get pending friend requests
    pending_requests = FriendRequest.query.filter_by(
        receiver_id=user_id, 
        status='pending'
    ).all()
    
    return render_template('social_feed.html', 
                         shared_workouts=shared_workouts,
                         pending_requests=pending_requests,
                         current_user=current_user)

@app.route('/friends')
@login_required
def friends_list():
    user_id = session['user_id']
    current_user = User.query.get(user_id)
    
    friends = current_user.get_friends()
    sent_requests = FriendRequest.query.filter_by(sender_id=user_id, status='pending').all()
    received_requests = FriendRequest.query.filter_by(receiver_id=user_id, status='pending').all()
    
    return render_template('friends.html', 
                         friends=friends,
                         sent_requests=sent_requests,
                         received_requests=received_requests)

@app.route('/search_users')
@login_required
def search_users():
    query = request.args.get('q', '')
    user_id = session['user_id']
    
    if query:
        users = User.query.filter(
            User.username.ilike(f'%{query}%'),
            User.id != user_id
        ).limit(10).all()
    else:
        users = []
    
    return render_template('search_users.html', users=users, query=query)

@app.route('/send_friend_request/<int:user_id>', methods=['POST'])
@login_required
def send_friend_request(user_id):
    sender_id = session['user_id']
    
    # Check if request already exists
    existing_request = FriendRequest.query.filter_by(
        sender_id=sender_id, 
        receiver_id=user_id
    ).first()
    
    if existing_request:
        flash('Friend request already sent!', 'warning')
    else:
        # Check if they're already friends
        reverse_request = FriendRequest.query.filter_by(
            sender_id=user_id, 
            receiver_id=sender_id,
            status='accepted'
        ).first()
        
        if reverse_request:
            flash('You are already friends!', 'warning')
        else:
            friend_request = FriendRequest(
                sender_id=sender_id,
                receiver_id=user_id,
                message=request.form.get('message', '')
            )
            db.session.add(friend_request)
            db.session.commit()
            flash('Friend request sent!', 'success')
    
    return redirect(request.referrer or url_for('search_users'))

@app.route('/respond_friend_request/<int:request_id>/<action>')
@login_required
def respond_friend_request(request_id, action):
    user_id = session['user_id']
    friend_request = FriendRequest.query.filter_by(
        id=request_id, 
        receiver_id=user_id
    ).first()
    
    if not friend_request:
        flash('Friend request not found!', 'error')
        return redirect(url_for('friends_list'))
    
    if action == 'accept':
        friend_request.status = 'accepted'
        flash(f'You are now friends with {friend_request.sender.username}!', 'success')
    elif action == 'decline':
        friend_request.status = 'declined'
        flash('Friend request declined.', 'info')
    
    friend_request.updated_at = datetime.utcnow()
    db.session.commit()
    
    return redirect(url_for('friends_list'))

@app.route('/share_workout/<int:workout_id>', methods=['GET', 'POST'])
@login_required
def share_workout(workout_id):
    user_id = session['user_id']
    workout = Workout.query.filter_by(id=workout_id, user_id=user_id).first()
    
    if not workout:
        flash('Workout not found!', 'error')
        return redirect(url_for('workouts'))
    
    if request.method == 'POST':
        # Check if already shared
        existing_share = WorkoutShare.query.filter_by(
            workout_id=workout_id,
            shared_by=user_id
        ).first()
        
        if existing_share:
            flash('Workout already shared!', 'warning')
        else:
            workout_share = WorkoutShare(
                workout_id=workout_id,
                shared_by=user_id,
                caption=request.form.get('caption', ''),
                is_public=request.form.get('is_public') == 'on'
            )
            db.session.add(workout_share)
            db.session.commit()
            flash('Workout shared successfully!', 'success')
        
        return redirect(url_for('social_feed'))
    
    return render_template('share_workout.html', workout=workout)

@app.route('/like_workout/<int:share_id>', methods=['POST'])
@login_required
def like_workout(share_id):
    user_id = session['user_id']
    
    # Check if already liked
    existing_like = WorkoutLike.query.filter_by(
        user_id=user_id,
        workout_share_id=share_id
    ).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        action = 'unliked'
    else:
        # Like
        like = WorkoutLike(
            user_id=user_id,
            workout_share_id=share_id
        )
        db.session.add(like)
        action = 'liked'
    
    db.session.commit()
    
    # Return JSON for AJAX requests
    if request.headers.get('Content-Type') == 'application/json':
        like_count = WorkoutLike.query.filter_by(workout_share_id=share_id).count()
        return jsonify({'action': action, 'like_count': like_count})
    
    return redirect(request.referrer or url_for('social_feed'))

@app.route('/comment_workout/<int:share_id>', methods=['POST'])
@login_required
def comment_workout(share_id):
    user_id = session['user_id']
    comment_text = request.form.get('comment')
    
    if comment_text:
        comment = WorkoutComment(
            user_id=user_id,
            workout_share_id=share_id,
            comment_text=comment_text
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment added!', 'success')
    
    return redirect(request.referrer or url_for('social_feed'))

@app.route('/fitness_goals')
@login_required
def fitness_goals():
    user_id = session['user_id']
    goals = FitnessGoal.query.filter_by(user_id=user_id).order_by(FitnessGoal.created_at.desc()).all()
    
    # Get friends' public goals
    current_user = User.query.get(user_id)
    friends = current_user.get_friends()
    friend_ids = [friend.id for friend in friends]
    
    friends_goals = FitnessGoal.query.filter(
        FitnessGoal.user_id.in_(friend_ids),
        FitnessGoal.is_public == True
    ).order_by(FitnessGoal.created_at.desc()).limit(10).all()
    
    return render_template('fitness_goals.html', goals=goals, friends_goals=friends_goals)

@app.route('/add_fitness_goal', methods=['GET', 'POST'])
@login_required
def add_fitness_goal():
    if request.method == 'POST':
        user_id = session['user_id']
        
        goal = FitnessGoal(
            user_id=user_id,
            title=request.form['title'],
            description=request.form.get('description', ''),
            target_value=float(request.form['target_value']) if request.form['target_value'] else None,
            unit=request.form.get('unit', ''),
            goal_type=request.form['goal_type'],
            target_date=datetime.strptime(request.form['target_date'], '%Y-%m-%d').date() if request.form['target_date'] else None,
            is_public=request.form.get('is_public') == 'on'
        )
        
        db.session.add(goal)
        db.session.commit()
        
        flash('Fitness goal created successfully!', 'success')
        return redirect(url_for('fitness_goals'))
    
    return render_template('add_fitness_goal.html')

@app.route('/update_goal_progress/<int:goal_id>', methods=['POST'])
@login_required
def update_goal_progress(goal_id):
    user_id = session['user_id']
    goal = FitnessGoal.query.filter_by(id=goal_id, user_id=user_id).first()
    
    if goal:
        goal.current_value = float(request.form['current_value'])
        
        # Check if goal is completed
        if goal.target_value and goal.current_value >= goal.target_value:
            goal.status = 'completed'
            flash(f'Congratulations! You completed your goal: {goal.title}!', 'success')
        
        goal.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Goal progress updated!', 'success')
    
    return redirect(url_for('fitness_goals'))

@app.route('/profile/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('social_feed'))
    
    current_user_id = session['user_id']
    current_user = User.query.get(current_user_id)
    
    # Check if users are friends or if profile is public
    is_friend = current_user.is_friend_with(user)
    can_view = user.is_profile_public or is_friend or user.id == current_user_id
    
    if not can_view:
        flash('This profile is private!', 'warning')
        return redirect(url_for('social_feed'))
    
    # Get recent workouts and goals
    recent_workouts = Workout.query.filter_by(user_id=user.id).order_by(Workout.date.desc()).limit(5).all()
    public_goals = FitnessGoal.query.filter_by(user_id=user.id, is_public=True).limit(3).all()
    
    return render_template('user_profile.html', 
                         profile_user=user, 
                         recent_workouts=recent_workouts,
                         public_goals=public_goals,
                         is_friend=is_friend,
                         current_user=current_user)

# PWA Routes
@app.route('/manifest.json')
def manifest():
    """Serve PWA manifest"""
    return app.send_static_file('manifest.json')

@app.route('/sw.js')
def service_worker():
    """Serve service worker"""
    response = make_response(app.send_static_file('sw.js'))
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

@app.route('/offline')
def offline():
    """Offline page for PWA"""
    return render_template('offline.html')

# API endpoints for mobile app
@app.route('/api/workout', methods=['POST'])
@login_required
def api_add_workout():
    """API endpoint for adding workouts from mobile"""
    try:
        data = request.get_json()
        
        workout = Workout(
            user_id=session['user_id'],
            exercise=data.get('exercise'),
            duration=int(data.get('duration', 0)),
            sets=int(data.get('sets', 0)),
            reps=int(data.get('reps', 0)),
            weight=float(data.get('weight', 0)),
            calories=int(data.get('calories', 0)),
            notes=data.get('notes', ''),
            date=datetime.utcnow()
        )
        
        db.session.add(workout)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Adventure logged successfully!',
            'workout_id': workout.id
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error logging adventure: {str(e)}'
        }), 400

@app.route('/api/workouts')
@login_required
def api_get_workouts():
    """API endpoint for getting workouts"""
    try:
        workouts = Workout.query.filter_by(user_id=session['user_id']).order_by(Workout.date.desc()).limit(10).all()
        
        workout_list = []
        for workout in workouts:
            workout_list.append({
                'id': workout.id,
                'exercise': workout.exercise,
                'duration': workout.duration,
                'sets': workout.sets,
                'reps': workout.reps,
                'weight': workout.weight,
                'calories': workout.calories,
                'notes': workout.notes,
                'date': workout.date.isoformat()
            })
        
        return jsonify({
            'success': True,
            'workouts': workout_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching workouts: {str(e)}'
        }), 400

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='0.0.0.0')
