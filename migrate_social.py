from app import app, db
import sqlite3

def migrate_database():
    """Add new columns to existing User table"""
    with app.app_context():
        # Get the database path
        db_path = 'instance/fitness_tracker.db'
        
        # Connect directly to SQLite to add columns
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Add new columns to User table
            cursor.execute('ALTER TABLE user ADD COLUMN bio TEXT')
            print("Added bio column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("bio column already exists")
            else:
                print(f"Error adding bio: {e}")
        
        try:
            cursor.execute('ALTER TABLE user ADD COLUMN profile_picture VARCHAR(200)')
            print("Added profile_picture column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("profile_picture column already exists")
            else:
                print(f"Error adding profile_picture: {e}")
        
        try:
            cursor.execute('ALTER TABLE user ADD COLUMN is_profile_public BOOLEAN DEFAULT 1')
            print("Added is_profile_public column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("is_profile_public column already exists")
            else:
                print(f"Error adding is_profile_public: {e}")
        
        try:
            cursor.execute('ALTER TABLE user ADD COLUMN fitness_goal VARCHAR(200)')
            print("Added fitness_goal column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("fitness_goal column already exists")
            else:
                print(f"Error adding fitness_goal: {e}")
        
        conn.commit()
        conn.close()
        
        # Now create all other new tables
        db.create_all()
        print("Created all new tables")

if __name__ == '__main__':
    migrate_database()
    print("Migration completed!")
