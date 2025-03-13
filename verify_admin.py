from app import app, db
from models import User

with app.app_context():
    user = User.query.filter_by(username='testuser').first()
    if user:
        print(f"Username: {user.username}, ID: {user.id}, Is Admin: {user.is_admin}")
        if not user.is_admin:
            user.is_admin = True
            db.session.commit()
            print("Updated testuser to admin")
    else:
        print("User 'testuser' not found - creating one")
        new_user = User(
            username='testuser',
            password=generate_password_hash('admin123'),
            email='testuser@example.com',
            is_admin=True
        )
        db.session.add(new_user)
        db.session.commit()
        print("Created testuser as admin")