from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy import text

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

# Add this with your other models
class FoodItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<FoodItem {self.name}>'

# Create tables
with app.app_context():
    db.create_all()

# Routes
def get_user_bookings():
    if 'user_id' in session:
        try:
            return Booking.query.filter_by(user_id=session['user_id']).all()
        except Exception as e:
            print(f"Error getting bookings: {str(e)}")
            return []
    return []

# Add the function to the template context
@app.context_processor
def utility_processor():
    return dict(get_user_bookings=get_user_bookings)

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
        food_items = FoodItem.query.order_by(FoodItem.category).all()
        return render_template('food_menu.html', food_items=food_items)
    except Exception as e:
        print(f"Error in food_menu: {str(e)}")
        return render_template('food_menu.html', food_items=[])

@app.route('/drinks_menu')
def drinks_menu():
    try:
        print("Attempting to fetch drink items...")
        drink_items = DrinkItem.query.order_by(DrinkItem.category).all()
        print(f"Found {len(drink_items)} drink items")
        
        if not drink_items:
            print("No drink items found in database")
            # Let's check if the table exists and has the right structure
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name='drink_item'"))
                if result.fetchone():
                    print("drink_item table exists")
                    # Check table structure
                    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='drink_item'"))
                    columns = [row[0] for row in result]
                    print("Table columns:", columns)
                else:
                    print("drink_item table does not exist")
                    
        return render_template('drinks_menu.html', drink_items=drink_items)
    except Exception as e:
        print(f"Error in drinks_menu: {str(e)}")
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
            return redirect(url_for('index'))  # Redirect to index page directly
        
        flash('Invalid username or password', 'error')
        return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                return jsonify({'error': 'Username already exists'}), 400
            
            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'Email already exists'}), 400

            # Create new user with hashed password
            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                password=hashed_password
            )

            # Add user to database
            db.session.add(new_user)
            db.session.commit()

            return jsonify({'message': 'User registered successfully'})

        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {str(e)}")
            return jsonify({'error': 'Registration failed'}), 500

    return render_template('register.html')

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
