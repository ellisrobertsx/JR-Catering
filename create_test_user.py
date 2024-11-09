from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_test_user(username='testuser2', password='testpass', email='test2@example.com'):
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User '{username}' already exists!")
            return existing_user
        
        # Create new user
        test_user = User(
            username=username,
            password=generate_password_hash(password),
            email=email
        )
        
        try:
            db.session.add(test_user)
            db.session.commit()
            print(f"Test user '{username}' created successfully!")
            return test_user
        except Exception as e:
            db.session.rollback()
            print(f"Error creating user: {str(e)}")
            return None

if __name__ == "__main__":
    user = create_test_user() 