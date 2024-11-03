from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy import text
from extensions import db
from models import User, MenuItem, DrinkItem, Booking, Contact, FoodItem
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Database configuration with better error handling
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    raise RuntimeError('DATABASE_URL environment variable is not set!')

# Convert postgres:// to postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

print(f"Using database URL: {database_url[:8]}...{database_url[-8:]}")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'dev')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize the db with the app
db.init_app(app)

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
    return {
        'datetime': datetime,
        'version': datetime.now().strftime('%Y%m%d-%H%M%S'),
        'get_user_bookings': get_user_bookings
    }

@app.route('/')
def index():
    logger.debug("Rendering index page")
    return render_template('index.html')

@app.route('/menu')
def menu():
    try:
        logger.debug("Fetching menu items")
        food_items = FoodItem.query.all()
        drink_items = DrinkItem.query.all()
        logger.debug(f"Found {len(food_items)} food items and {len(drink_items)} drink items")
        return render_template('menu.html', food_items=food_items, drink_items=drink_items)
    except Exception as e:
        logger.error(f"Error in menu: {str(e)}")
        return render_template('menu.html', food_items=[], drink_items=[])

@app.route('/food_menu')
def food_menu():
    try:
        # Get all food items and group by category in the desired order
        categories = ['Starters', 'Mains', 'Desserts']
        food_items = FoodItem.query.all()
        
        # Create a dictionary to store items by category
        menu_items = {}
        for category in categories:
            menu_items[category] = [item for item in food_items if item.category == category]
        
        # Debug print
        print(f"Found {len(food_items)} food items")
        for category, items in menu_items.items():
            print(f"{category}: {len(items)} items")
            
        return render_template('food_menu.html', menu_items=menu_items)
    except Exception as e:
        print(f"Error in food_menu route: {str(e)}")
        return render_template('food_menu.html', menu_items={})

@app.route('/drinks_menu')
def drinks_menu():
    try:
        print("Attempting to fetch drink items...")
        drink_items = DrinkItem.query.order_by(DrinkItem.category).all()
        print(f"Found {len(drink_items)} drink items")
        
        # Group items by category
        menu_items = {}
        for item in drink_items:
            if item.category not in menu_items:
                menu_items[item.category] = []
            menu_items[item.category].append(item)
        
        return render_template('drinks_menu.html', menu_items=menu_items)
    except Exception as e:
        print(f"Error in drinks_menu: {str(e)}")
        return render_template('drinks_menu.html', menu_items={})

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    if 'user_id' not in session:
        flash('Please login to make a booking', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            new_booking = Booking(
                user_id=session['user_id'],
                name=request.form['name'],
                email=request.form['email'],
                phone=request.form['phone'],
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                time=request.form['time'],
                guests=int(request.form['guests']),
                special_requests=request.form.get('special-requests', '')
            )
            db.session.add(new_booking)
            db.session.commit()
            
            return render_template('booking_confirmation.html', booking=new_booking)
        except Exception as e:
            print(f"Booking error: {str(e)}")
            flash('Error creating booking. Please try again.', 'error')
            db.session.rollback()
    
    user_bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    return render_template('book.html', bookings=user_bookings)

@app.route('/edit_booking/<int:booking_id>', methods=['POST'])
def edit_booking(booking_id):
    # Check if user is logged in
    if 'user_id' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Please login to continue'}), 401
        return redirect(url_for('login'))

    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Verify booking belongs to user
        if booking.user_id != session['user_id']:
            return jsonify({'error': 'Unauthorized access'}), 403

        # Update booking details
        booking.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        booking.time = request.form['time']
        booking.guests = int(request.form['guests'])
        booking.special_requests = request.form.get('special-requests', '')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'date': booking.date.strftime('%Y-%m-%d'),
            'time': booking.time,
            'guests': booking.guests,
            'special_requests': booking.special_requests
        })

    except Exception as e:
        db.session.rollback()
        print(f"Edit booking error: {str(e)}")
        return jsonify({'error': 'Failed to update booking'}), 500

@app.route('/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401

    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        db.session.delete(booking)
        db.session.commit()
        flash('Booking cancelled successfully!', 'success')
    except Exception as e:
        print(f"Delete booking error: {str(e)}")
        db.session.rollback()
        flash('Error cancelling booking', 'error')
    
    return redirect(url_for('book'))

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

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
