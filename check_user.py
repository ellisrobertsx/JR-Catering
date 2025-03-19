from app import app, db
from models import User
from passlib.hash import sha256_crypt

def check_user():
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        if user:
            user.password = sha256_crypt.hash('admin123')
            user.is_admin = True
            db.session.commit()
            print(f"Updated {user.username} to admin with password 'admin123'!")
        else:
            new_user = User(
                username='testuser',
                email='testuser@example.com',
                password=sha256_crypt.hash('admin123'),
                is_admin=True
            )
            db.session.add(new_user)
            db.session.commit()
            print("Created new admin user 'testuser' with password 'admin123'!")
        print("IMPORTANT: Change this password after login!")

if __name__ == "__main__":
    check_user()