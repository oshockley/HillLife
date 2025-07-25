#!/usr/bin/env python3
"""
FitTracker Pro Setup Script
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required Python packages"""
    print("🔥 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements!")
        return False

def initialize_database():
    """Initialize the database"""
    print("🗄️ Initializing database...")
    try:
        from app import app, db, init_db
        with app.app_context():
            init_db()
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def main():
    """Main setup function"""
    print("🏋️‍♂️ WELCOME TO FITTRACKER PRO SETUP")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Please run this script from the FitTracker directory!")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    print("\n🎉 SETUP COMPLETE!")
    print("=" * 50)
    print("🚀 To start the application, run:")
    print("   python app.py")
    print("\n💪 Ready to DOMINATE your fitness journey!")

if __name__ == "__main__":
    main()
