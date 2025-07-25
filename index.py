# Vercel WSGI Handler
from app import app

# This is needed for Vercel to serve your Flask app
if __name__ == "__main__":
    app.run()
