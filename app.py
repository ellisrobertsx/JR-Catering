from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Database configuration with better error handling
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    raise RuntimeError('DATABASE_URL environment variable is not set!')

# Convert postgres:// to postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

print(f"Using database URL: {database_url[:8]}...{database_url[-8:]}")  # Log partial URL for debugging

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'dev')

db = SQLAlchemy(app)

# Import models
from models import User, MenuItem, DrinkItem, Booking, Contact

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    food_items = MenuItem.query.filter_by(category='food').all()
    drink_items = MenuItem.query.filter_by(category='drink').all()
    return render_template('menu.html', food_items=food_items, drink_items=drink_items)

@app.route('/food_menu')
def food_menu():
    try:
        food_items = MenuItem.query.filter_by(category='food').all()
        print("DEBUG - Food Items Found:", [{"name": item.name, "category": item.category} for item in food_items])
        return render_template('food_menu.html', food_items=food_items)
    except Exception as e:
        print("DEBUG - Error in food_menu:", str(e))
        return render_template('food_menu.html', food_items=[])

@app.route('/drinks_menu')
def drinks_menu():
    try:
        drink_items = DrinkItem.query.order_by(DrinkItem.category).all()
        print("DEBUG - Drink Items Found:")
        for item in drink_items:
            print(f"- {item.name} ({item.category}): £{item.price}")
        return render_template('drinks_menu.html', drink_items=drink_items)
    except Exception as e:
        print("DEBUG - Error in drinks_menu:", str(e))
        return render_template('drinks_menu.html', drink_items=[])

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route('/book')
def book():
    return render_template('book.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))