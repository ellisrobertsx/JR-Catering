from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy import text
from extensions import db
from models import User, MenuItem, DrinkItem, Booking, Contact, FoodItem
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory, g
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from models import Booking
from flask_compress import Compress
from flask_caching import Cache
from PIL import Image
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from passlib.hash import scrypt
from functools import wraps
from dotenv import load_dotenv
import psycopg2

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'index'  # Redirect to index instead of login

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Use the Railway database URL
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
    SQLALCHEMY_DATABASE_URI='postgresql://postgres:qXoNbwivQCAIEWbwBOjIZoSmhdMIOvOM@junction.proxy.rlwy.net:44318/railway',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)

# Login decorator from auth.py
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/food_menu')
def food_menu():
    try:
        # Test connection before query
        if not test_connection():
            raise Exception("Could not connect to database")
            
        food_items = FoodItem.query.all()
        menu_items = {}
        for item in food_items:
            if item.category not in menu_items:
                menu_items[item.category] = []
            menu_items[item.category].append(item)
        return render_template('food_menu.html', menu_items=menu_items)
    except Exception as e:
        print(f"Database error: {str(e)}")
        return render_template('food_menu.html', menu_items={})

@app.route('/drinks_menu')
def drinks_menu():
    try:
        drink_items = DrinkItem.query.all()
        menu_items = {}
        for item in drink_items:
            if item.category not in menu_items:
                menu_items[item.category] = []
            menu_items[item.category].append(item)
        return render_template('drinks_menu.html', menu_items=menu_items)
    except Exception as e:
        print(f"Database error: {str(e)}")
        return render_template('drinks_menu.html', menu_items={})

@app.route('/menu')
def menu():
    menu_items = MenuItem.query.all()
    return render_template('menu.html', menu_items=menu_items)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        new_contact = Contact(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()
        
        flash('Message sent successfully!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        date = request.form.get('date')
        time = request.form.get('time')
        guests = request.form.get('guests')
        
        new_booking = Booking(name=name, email=email, date=date, time=time, guests=guests)
        db.session.add(new_booking)
        db.session.commit()
        
        flash('Booking submitted successfully!', 'success')
        return redirect(url_for('book'))
    
    return render_template('book.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/admin')
def admin_panel():
    # Simple admin check without requiring login
    return render_template('admin_panel.html', 
                         menu_items=MenuItem.query.all(),
                         food_items=FoodItem.query.all(),
                         drink_items=DrinkItem.query.all(),
                         bookings=Booking.query.order_by(Booking.date.desc()).all(),
                         messages=Contact.query.order_by(Contact.id.desc()).all())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        
        flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/test-connection')
def test_connection():
    try:
        # Test basic database connection
        result = db.session.execute('SELECT 1').fetchone()
        
        # Test if we can fetch food items
        food_count = FoodItem.query.count()
        drink_count = DrinkItem.query.count()
        
        return jsonify({
            'status': 'Connected',
            'database_test': bool(result),
            'food_items_count': food_count,
            'drink_items_count': drink_count
        })
    except Exception as e:
        print("Connection error:", str(e))
        return jsonify({
            'status': 'Error',
            'message': str(e)
        })

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        print("Setting up database and booking system...")
        try:
            # Create all tables
            db.create_all()
            
            # First create a test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password='testpass',
                is_admin=False
            )
            db.session.add(test_user)
            db.session.commit()
            
            # Now create booking with the new user's ID
            test_booking = Booking(
                user_id=test_user.id,  # Use the newly created user's ID
                name='Test Customer',
                email='test@example.com',
                phone='1234567890',
                date='2024-03-20',
                time='18:00',
                guests=4,
                special_requests='Test booking request'
            )
            
            db.session.add(test_booking)
            db.session.commit()
            print("✅ Database tables and booking system set up successfully!")
            
        except Exception as e:
            print(f"❌ Error setting up booking system: {str(e)}")
            db.session.rollback()
            
    app.run(debug=True)

