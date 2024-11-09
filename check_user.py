from app import app, db
from models import User

def check_user(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User found:")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Password hash: {user.password}")
        else:
            print(f"No user found with username: {username}")

if __name__ == "__main__":
    username_to_check = input("Enter username to check: ")
    check_user(username_to_check) 