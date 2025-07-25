# Hill Life 🏔️
*Reach Your Pinnacle*

A modern fitness tracking Progressive Web App designed to help you conquer your fitness goals like climbing a mountain. Built with Flask, featuring a beautiful sunset gradient theme, social features, and mobile-optimized experience.

![Hill Life](static/icons/icon-512x512.png)

## ✨ Features

### 🏔️ Core Fitness Tracking
- **Adventure Logging**: Track workouts with detailed metrics (sets, reps, weight, duration)
- **Progress Dashboard**: Visualize your fitness journey with interactive charts
- **BMI Tracking**: Monitor health metrics over time
- **Goal Setting**: Set and track summit goals for motivation

### 🌐 Social Community
- **Climbing Partners**: Connect with friends and fitness enthusiasts
- **Workout Sharing**: Share your adventures with the community
- **Social Feed**: Like and comment on friends' achievements
- **Friend Requests**: Build your fitness network

### 📱 Mobile-First Design
- **Progressive Web App**: Install on iOS and Android devices
- **Offline Support**: Log workouts even without internet
- **Touch-Optimized**: Designed for mobile interaction
- **Responsive**: Beautiful on all screen sizes

### 🎨 Premium Experience
- **Animated Gradients**: Eye-catching moving background
- **Click Sounds**: Satisfying audio feedback
- **Mountain Theme**: Consistent adventure-focused branding
- **Modern UI**: Bootstrap 5 with custom styling

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/hill-life.git
   cd hill-life
   ```

2. **Install dependencies**
   ```bash
   pip install flask flask-sqlalchemy flask-bcrypt flask-jwt-extended pillow
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   ```
   http://localhost:5000
   ```

### 📱 Mobile Installation

#### Android:
1. Open Chrome and visit your Hill Life URL
2. Tap "Install App" when prompted
3. App installs to home screen!

#### iOS:
1. Open Safari and visit your Hill Life URL
2. Tap Share → "Add to Home Screen"
3. App appears on home screen with icon!

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, Chart.js, Font Awesome
- **Authentication**: Flask-Bcrypt, JWT tokens
- **PWA**: Service Worker, Web App Manifest
- **Icons**: Custom generated mountain-themed icons

## 🎯 API Endpoints

### Authentication
- `POST /register` - Create new account
- `POST /login` - User login
- `GET /logout` - User logout

### Workouts
- `GET /workouts` - View all adventures
- `POST /add_workout` - Log new adventure
- `POST /api/workout` - API endpoint for mobile

### Social Features
- `GET /social_feed` - Community feed
- `POST /send_friend_request` - Send friend request
- `POST /share_workout` - Share adventure

### PWA
- `GET /manifest.json` - App manifest
- `GET /sw.js` - Service worker
- `GET /offline` - Offline page

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🏔️ About Hill Life

Hill Life is more than just a fitness tracker - it's a journey to reach your pinnacle. Every workout is an adventure, every goal is a summit to conquer, and every friend is a climbing partner on your path to greatness.

**Reach Your Pinnacle** 🎯

---

Built with ❤️ for fitness enthusiasts everywhere
