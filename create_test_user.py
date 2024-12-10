from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # Check if user with ID 1 exists
        admin = User.query.get(1)
        if admin:
            print(f"Admin user already exists with username: {admin.username}")
            return admin
        
        # Create admin user with ID 1
        admin_user = User(
            id=1,  # This will be your admin ID
            username='admin',
            password=generate_password_hash('admin123'),  # Change this password!
            email='admin@example.com'
        )
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            print("""
Admin user created successfully!
Username: admin
Password: admin123
            
IMPORTANT: Please change these credentials after first login!
            """)
            return admin_user
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin: {str(e)}")
            return None

if __name__ == "__main__":
    create_admin() 