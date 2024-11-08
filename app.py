from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy import text
from extensions import db
from models import User, MenuItem, DrinkItem, Booking, Contact, FoodItem
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from models import Booking
from flask_compress import Compress
from flask_caching import Cache
from PIL import Image

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_user_bookings():
    if 'user_id' not in session:
        return False
    try:
        booking = Booking.query.filter_by(user_id=session['user_id']).first()
        return booking is not None
    except Exception as e:
        print(f"Error in get_user_bookings: {str(e)}")
        return False

app = Flask(__name__)

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    raise RuntimeError('DATABASE_URL environment variable is not set!')

if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'dev')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize extensions
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

app.jinja_env.globals.update(get_user_bookings=get_user_bookings)

# Initialize compression
compress = Compress()

# Configure caching
cache = Cache(config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Enable compression
compress.init_app(app)
cache.init_app(app)

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Cache static assets
    if request.path.startswith('/static/'):
        response.cache_control.max_age = 31536000  # 1 year
        response.cache_control.public = True
        
    return response

# Routes
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
    if request.method == 'POST':
        try:
            print("Received contact form submission")
            # Get form data
            name = request.form['name']
            phone = request.form['phone']
            email = request.form['email']
            message = request.form['message']
            
            print(f"Form data: {name}, {email}, {phone}, {message}")

            # Create new contact entry
            new_contact = Contact(
                name=name,
                phone=phone,
                email=email,
                message=message
            )

            # Save to database
            db.session.add(new_contact)
            db.session.commit()
            print("Successfully saved contact form submission")

            flash('Thank you for your message! We will get back to you soon.', 'success')
            return redirect(url_for('contact'))

        except Exception as e:
            print(f"Error saving contact form: {str(e)}")
            db.session.rollback()
            flash('Sorry, there was an error sending your message. Please try again.', 'error')
            return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/book')
def book():
    if 'user_id' not in session:
        return render_template('book.html')
    
    # Get user's bookings
    bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    return render_template('book.html', bookings=bookings)

@app.route('/create_booking', methods=['POST'])
def create_booking():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login to make a booking'}), 401

    try:
        data = request.get_json()
        logger.info(f"Received booking data: {data}")
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'date', 'time', 'guests']
        if not all(key in data for key in required_fields):
            missing_fields = [field for field in required_fields if field not in data]
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Create new booking
        new_booking = Booking(
            user_id=session['user_id'],
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            time=data['time'],
            guests=int(data['guests']),
            special_requests=data.get('special_requests', '')
        )
        
        db.session.add(new_booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'booking': {
                'id': new_booking.id,
                'name': new_booking.name,
                'email': new_booking.email,
                'phone': new_booking.phone,
                'date': data['date'],
                'time': data['time'],
                'guests': data['guests']
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating booking: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/edit_booking/<int:booking_id>', methods=['POST'])
def edit_booking(booking_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401

    try:
        data = request.get_json()
        booking = Booking.query.get_or_404(booking_id)
        
        if booking.user_id != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403

        booking.name = data['name']
        booking.email = data['email']
        booking.phone = data['phone']
        booking.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        booking.time = data['time']
        booking.guests = int(data['guests'])
        
        db.session.commit()

        return jsonify({
            'success': True,
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'date': data['date'],
            'time': data['time'],
            'guests': data['guests']
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Please login'}), 401

    try:
        booking = Booking.query.get_or_404(booking_id)
        if booking.user_id != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403

        db.session.delete(booking)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel booking'}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Please provide both username and password', 'error')
                return redirect(url_for('login'))
            
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.username
                flash('Successfully logged in!', 'success')
                return redirect(url_for('index'))
            
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login', 'error')
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
            confirm_password = request.form['confirm_password']

            # Check if passwords match
            if password != confirm_password:
                return jsonify({'error': 'Passwords do not match'}), 400

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
    return render_template('500.html'), 500


@app.route('/check_db')
def check_db():
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM bookings LIMIT 0;"))
            columns = result.keys()
            return jsonify({
                'columns': list(columns)
            })
    except Exception as e:
        print(f"Error in check_db: {str(e)}")
        return str(e)

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

def optimize_images():
    img_dir = os.path.join('static', 'assets', 'images')
    for filename in os.listdir(img_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(img_dir, filename)
            with Image.open(img_path) as img:
                webp_path = os.path.splitext(img_path)[0] + '.webp'
                img.save(webp_path, 'WEBP', quality=85)
                
                if img.size[0] > 1200 or img.size[1] > 1200:
                    img.thumbnail((1200, 1200), Image.LANCZOS)
                    img.save(img_path, quality=85, optimize=True)

@app.after_request
def add_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    else:
        response.headers['Cache-Control'] = 'public, max-age=300'
    
    return response

# Serve service worker
@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static/assets/js', 'service-worker.js')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

