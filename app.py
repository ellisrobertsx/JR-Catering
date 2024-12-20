from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy import text
from extensions import db
from models import User, MenuItem, DrinkItem, Booking, Contact, FoodItem
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory, g
from models import Booking
from flask_compress import Compress
from flask_caching import Cache
from PIL import Image
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from passlib.hash import scrypt
from functools import wraps

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')

app.debug = False

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_bookings():
    if 'user_id' in session:
        return Booking.query.filter_by(user_id=session['user_id']).first() is not None
    return False



# Database configuration
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    raise RuntimeError('DATABASE_URL environment variable is not set!')

if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    SESSION_REFRESH_EACH_REQUEST=True
)

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

@app.before_request
def before_request():
    # Ensure user session is valid
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user is None:
            session.clear()

@app.context_processor
def inject_user():
    return dict(
        user=getattr(g, 'user', None)
    )

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    if request.path.startswith('/static/'):
        response.cache_control.max_age = 31536000  # 1 year
        response.cache_control.public = True
        
    return response

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

# Routes
@app.route('/')
@app.route('/index')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user is None:
            session.clear()
    
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
        categories = ['Starters', 'Mains', 'Desserts']
        food_items = FoodItem.query.all()
        
        menu_items = {}
        for category in categories:
            menu_items[category] = [item for item in food_items if item.category == category]
        
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
            name = request.form['name']
            phone = request.form['phone']
            email = request.form['email']
            message = request.form['message']
            
            print(f"Form data: {name}, {email}, {phone}, {message}")

            new_contact = Contact(
                name=name,
                phone=phone,
                email=email,
                message=message
            )

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

    return render_template('contact.html', session=session)

@app.route('/book')
def book():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    
    bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    return render_template('book.html', bookings=bookings)

@app.route('/create_booking', methods=['POST'])
@login_required
def create_booking():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login to continue'}), 401
        
    try:
        data = request.get_json()
        logger.info(f"Received booking data: {data}")
        
        required_fields = ['name', 'email', 'phone', 'date', 'time', 'guests']
        if not all(key in data for key in required_fields):
            missing_fields = [field for field in required_fields if field not in data]
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

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
        return jsonify({'error': 'Failed to create booking'}), 500

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
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session.clear()
            session['user_id'] = user.id
            # Redirect to admin panel if user is admin
            if user.id == 1:
                return redirect(url_for('admin_panel'))
            return redirect(url_for('index'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    g.user = None
    
    response = redirect(url_for('index'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            # Validate input
            if not username or not email or not password:
                return jsonify({'error': 'All fields are required'}), 400

            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                return jsonify({'error': 'Username already exists'}), 400
            
            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'Email already exists'}), 400

            # Create new user with werkzeug's password hashing
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(
                username=username,
                email=email,
                password=hashed_password
            )

            db.session.add(new_user)
            db.session.commit()

            print(f"User registered successfully: {username}")
            return jsonify({'success': 'Registration successful'}), 200

        except Exception as e:
            print(f"Registration error: {str(e)}")
            db.session.rollback()
            return jsonify({'error': 'Registration failed. Please try again.'}), 500

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

@app.after_request
def add_header(response):
    # Prevent caching of dynamic pages
    if request.endpoint != 'static':
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
    return response

# ... existing imports ...

# Add this after your other routes
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    # Check if user is admin (user_id = 1)
    if session.get('user_id') != 1:
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    
    # Get all data for admin
    menu_items = MenuItem.query.all()
    food_items = FoodItem.query.all()
    drink_items = DrinkItem.query.all()
    bookings = Booking.query.order_by(Booking.date.desc()).all()
    messages = Contact.query.order_by(Contact.id.desc()).all()
    
    return render_template('admin_panel.html', 
                         menu_items=menu_items,
                         food_items=food_items,
                         drink_items=drink_items,
                         bookings=bookings,
                         messages=messages)

@app.route('/admin_menu', methods=['GET', 'POST'])
@login_required
def admin_menu():
    # Check if user is admin (user_id = 1)
    if session.get('user_id') != 1:
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        menu_type = request.form.get('menu_type')
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        
        if menu_type == 'food':
            category = request.form.get('category')
            new_item = FoodItem(name=name, description=description, price=price, category=category)
        else:
            category = request.form.get('drink_category')
            new_item = DrinkItem(name=name, description=description, price=price, category=category)
            
        db.session.add(new_item)
        db.session.commit()
        flash('Menu item added successfully!', 'success')
        return redirect(url_for('admin_panel'))
        
    return render_template('admin_menu.html')

@app.route('/admin/update_item', methods=['POST'])
@login_required
def update_item():
    if session.get('user_id') != 1:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        item_type = data.get('type')
        item_id = data.get('id')
        
        if item_type == 'food':
            item = FoodItem.query.get(item_id)
        else:
            item = DrinkItem.query.get(item_id)
            
        if item:
            item.name = data.get('name')
            item.description = data.get('description')
            item.category = data.get('category')
            item.price = float(data.get('price'))
            
            db.session.commit()
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Item not found'}), 404
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/toggle_message_read', methods=['POST'])
@login_required
def toggle_message_read():
    if session.get('user_id') != 1:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        message_id = data.get('message_id')
        is_read = data.get('is_read')
        
        message = Contact.query.get(message_id)
        if message:
            message.is_read = is_read
            db.session.commit()
            return jsonify({'success': True})
            
        return jsonify({'success': False, 'error': 'Message not found'}), 404
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/delete_message', methods=['POST'])
@login_required
def delete_message():
    if session.get('user_id') != 1:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        message_id = data.get('message_id')
        
        message = Contact.query.get(message_id)
        if message:
            db.session.delete(message)
            db.session.commit()
            return jsonify({'success': True})
            
        return jsonify({'success': False, 'error': 'Message not found'}), 404
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

