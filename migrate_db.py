#!/usr/bin/env python3
"""
Database Migration Script for FitTracker Pro
Adds new walking/cardio tracking fields to existing database
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add new columns to existing workout table"""
    db_path = 'fitness_tracker.db'
    
    if not os.path.exists(db_path):
        print("✅ No existing database found. New database will be created with all fields.")
        return True
    
    print("🔄 Migrating existing database...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if new columns already exist
        cursor.execute("PRAGMA table_info(workout)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = ['speed', 'incline', 'distance', 'avg_heart_rate', 'workout_type']
        columns_to_add = [col for col in new_columns if col not in columns]
        
        if not columns_to_add:
            print("✅ Database already up to date!")
            conn.close()
            return True
        
        # Add missing columns
        for column in columns_to_add:
            if column == 'workout_type':
                cursor.execute(f"ALTER TABLE workout ADD COLUMN {column} VARCHAR(20) DEFAULT 'strength'")
            elif column == 'avg_heart_rate':
                cursor.execute(f"ALTER TABLE workout ADD COLUMN {column} INTEGER")
            else:
                cursor.execute(f"ALTER TABLE workout ADD COLUMN {column} FLOAT")
            print(f"✅ Added column: {column}")
        
        conn.commit()
        conn.close()
        print("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🏋️‍♂️ FitTracker Pro Database Migration")
    print("=" * 40)
    
    if migrate_database():
        print("\n🚀 Ready to start FitTracker Pro!")
    else:
        print("\n💥 Migration failed. Please check the error above.")
