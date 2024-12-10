from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def make_admin():
    with app.app_context():
        # Get user with ID 1
        user = User.query.get(1)
        if user:
            # Update their password
            user.password = generate_password_hash('admin123')
            db.session.commit()
            print(f"""
User {user.username} is now admin!
Password has been set to: admin123

IMPORTANT: Please change this password after login!
            """)
        else:
            print("No user found with ID 1")

if __name__ == "__main__":
    make_admin() 