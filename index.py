# Vercel WSGI Handler
import os
os.environ['VERCEL_ENV'] = '1'  # Set Vercel environment flag

from app import app, db, init_db

# Initialize database on first import
with app.app_context():
    init_db()

# This is needed for Vercel to serve your Flask app
if __name__ == "__main__":
    app.run()
