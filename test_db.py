from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
import os

app = Flask(__name__)

database_url = "postgres://uahl64ocac54vj:p5342a746bcc924b8263b1db85dd318543649ae3b749d3172444d051382f285aa@cbdhrtd93854d5.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d5e8o09ku16d72"

# Convert postgres:// to postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

print("\n=== Database Connection Test ===")
print("Attempting to connect to database...")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.Date)
    time = db.Column(db.String(5))
    guests = db.Column(db.Integer)

def test_connection():
    try:
        with app.app_context():
            # Test 1: Check if tables exist
            print("\n1. Checking existing tables...")
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Found tables: {tables}")

            # Test 2: Check Users
            print("\n2. Checking Users table...")
            if 'users' in tables:
                users = User.query.all()
                print(f"Found {len(users)} users")
                for user in users:
                    print(f"User ID: {user.id}, Username: {user.username}, Email: {user.email}")
            else:
                print("Users table not found!")

            # Test 3: Check Bookings
            print("\n3. Checking Bookings table...")
            if 'bookings' in tables:
                bookings = Booking.query.all()
                print(f"Found {len(bookings)} bookings")
                for booking in bookings:
                    print(f"Booking ID: {booking.id}, User ID: {booking.user_id}, "
                          f"Date: {booking.date}, Time: {booking.time}, Guests: {booking.guests}")
            else:
                print("Bookings table not found!")

            print("\n=== Connection Test Completed Successfully ===")

    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        raise

if __name__ == "__main__":
    test_connection() 