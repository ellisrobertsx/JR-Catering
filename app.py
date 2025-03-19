from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy import text
from extensions import db
from models import User, MenuItem, DrinkItem, Booking, Contact, FoodItem
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory, g, make_response
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_compress import Compress
from flask_caching import Cache
from PIL import Image
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from passlib.hash import scrypt
from passlib.hash import sha256_crypt  # Added for dual-hash support
from functools import wraps
from dotenv import load_dotenv
import psycopg2
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import urlparse  # Added missing import

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('app.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'

app = Flask(__name__)

# Load environment variables
load_dotenv()

app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
    SQLALCHEMY_DATABASE_URI='postgresql://postgres:qXoNbwivQCAIEWbwBOjIZoSmhdMIOvOM@junction.proxy.rlwy.net:44318/railway',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(days=31),
    REMEMBER_COOKIE_DURATION=timedelta(days=31),
    REMEMBER_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    REMEMBER_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST=True,
    SEND_FILE_MAX_AGE_DEFAULT=0,
    TEMPLATES_AUTO_RELOAD=True
)

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.remember_cookie_duration = timedelta(days=31)

@login_manager.user_loader
def load_user(user_id):
    try:
        logger.debug(f"Loading user with ID: {user_id}")
        user = User.query.get(int(user_id))
        if user:
            logger.debug(f"User {user.username} loaded successfully")
        else:
            logger.warning(f"No user found with ID: {user_id}")
        return user
    except Exception as e:
        logger.error(f"Error loading user {user_id}: {str(e)}")
        return None

# Serve static files
@app.route('/manifest.json')
def serve_manifest():
    try:
        return send_from_directory('static', 'manifest.json')
    except Exception as e:
        logger.error(f"Error serving manifest.json: {str(e)}")
        return jsonify({'error': 'Manifest not found'}), 404

@app.route('/favicon.ico')
def serve_favicon():
    try:
        return send_from_directory('static', 'favicon.ico')
    except Exception as e:
        logger.error(f"Error serving favicon.ico: {str(e)}")
        return jsonify({'error': 'Favicon not found'}), 404

# Routes
@app.route('/')
def index():
    try:
        logger.debug(f"Index route - User authenticated: {current_user.is_authenticated}")
        if current_user.is_authenticated:
            logger.debug(f"User {current_user.username} is authenticated")
        response = make_response(render_template('index.html'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        logger.error(f"Error loading index: {str(e)}")
        return render_template('500.html'), 500

@app.route('/food_menu')
def food_menu():
    try:
        logger.debug(f"Food_menu route - User authenticated: {current_user.is_authenticated}")
        food_items = FoodItem.query.all()
        logger.debug(f"Retrieved {len(food_items)} food items from database")
        if not food_items:
            logger.warning("No food items found in database")
            flash('No food items available yet.', 'info')
        menu_items = {}
        for item in food_items:
            if item.category not in menu_items:
                menu_items[item.category] = []
            menu_items[item.category].append(item)
        return render_template('food_menu.html', menu_items=menu_items)
    except Exception as e:
        logger.error(f"Database error in food_menu: {str(e)}")
        flash('Error loading food menu. Please try again later.', 'error')
        return render_template('food_menu.html', menu_items={})

@app.route('/drinks_menu')
def drinks_menu():
    try:
        logger.debug(f"Drinks_menu route - User authenticated: {current_user.is_authenticated}")
        drink_items = DrinkItem.query.all()
        logger.debug(f"Retrieved {len(drink_items)} drink items from database")
        if not drink_items:
            logger.warning("No drink items found in database")
            flash('No drink items available yet.', 'info')
        menu_items = {}
        for item in drink_items:
            if item.category not in menu_items:
                menu_items[item.category] = []
            menu_items[item.category].append(item)
        return render_template('drinks_menu.html', menu_items=menu_items)
    except Exception as e:
        logger.error(f"Database error in drinks_menu: {str(e)}")
        flash('Error loading drinks menu. Please try again later.', 'error')
        return render_template('drinks_menu.html', menu_items={})

@app.route('/menu')
def menu():
    try:
        logger.debug(f"Menu route - User authenticated: {current_user.is_authenticated}")
        menu_items = MenuItem.query.all()
        return render_template('menu.html', menu_items=menu_items)
    except Exception as e:
        logger.error(f"Error loading menu: {str(e)}")
        flash('Error loading menu. Please try again later.', 'error')
        return render_template('menu.html', menu_items=[])

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    try:
        logger.debug(f"Contact route - User authenticated: {current_user.is_authenticated}")
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')
            if not name or not email or not message:
                flash('Please fill in all fields.', 'error')
                return render_template('contact.html')
            new_contact = Contact(name=name, email=email, message=message)
            db.session.add(new_contact)
            db.session.commit()
            flash('Message sent successfully!', 'success')
            return redirect(url_for('contact'))
        return render_template('contact.html')
    except Exception as e:
        logger.error(f"Error in contact: {str(e)}")
        flash('Error processing your message. Please try again later.', 'error')
        return render_template('contact.html')

@app.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    try:
        logger.debug(f"Book route - User authenticated: {current_user.is_authenticated}, ID: {current_user.id}")
        bookings = Booking.query.filter_by(user_id=current_user.id).all()
        return render_template('book.html', bookings=bookings)
    except Exception as e:
        logger.error(f"Error in book: {str(e)}")
        flash('Error processing your booking. Please try again later.', 'error')
        return render_template('book.html', bookings=[])

@app.route('/create_booking', methods=['POST'])
@login_required
def create_booking():
    try:
        logger.debug(f"Create_booking route - User authenticated: {current_user.is_authenticated}")
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        date = data.get('date')
        time = data.get('time')
        guests = data.get('guests')
        special_requests = data.get('special_requests', '')

        if not all([name, email, phone, date, time, guests]):
            return jsonify({'error': 'All required fields must be filled'}), 400

        new_booking = Booking(
            user_id=current_user.id,
            name=name,
            email=email,
            phone=phone,
            date=date,
            time=time,
            guests=int(guests),
            special_requests=special_requests
        )
        db.session.add(new_booking)
        db.session.commit()
        logger.debug(f"New booking created: ID {new_booking.id}")

        return jsonify({
            'success': 'Booking created successfully',
            'booking': {
                'id': new_booking.id,
                'name': new_booking.name,
                'email': new_booking.email,
                'phone': new_booking.phone,
                'date': new_booking.date,
                'time': new_booking.time,
                'guests': new_booking.guests
            }
        })
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in create_booking: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in create_booking: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/edit_booking/<int:booking_id>', methods=['POST'])
@login_required
def edit_booking(booking_id):
    try:
        logger.debug(f"Edit_booking route - User authenticated: {current_user.is_authenticated}")
        booking = Booking.query.get_or_404(booking_id)
        if booking.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()
        booking.name = data.get('name', booking.name)
        booking.email = data.get('email', booking.email)
        booking.phone = data.get('phone', booking.phone)
        booking.date = data.get('date', booking.date)
        booking.time = data.get('time', booking.time)
        booking.guests = int(data.get('guests', booking.guests))
        db.session.commit()
        return jsonify({'success': 'Booking updated successfully'})
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in edit_booking: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in edit_booking: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/delete_booking/<int:booking_id>', methods=['POST'])
@login_required
def delete_booking(booking_id):
    try:
        logger.debug(f"Delete_booking route - User authenticated: {current_user.is_authenticated}")
        booking = Booking.query.get_or_404(booking_id)
        if booking.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        db.session.delete(booking)
        db.session.commit()
        return jsonify({'success': 'Booking deleted successfully'})
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in delete_booking: {str(e)}")
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in delete_booking: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/confirmation/<int:booking_id>')
@login_required
def confirmation(booking_id):
    try:
        logger.debug(f"Confirmation route - User authenticated: {current_user.is_authenticated}")
        booking = Booking.query.get_or_404(booking_id)
        if booking.user_id != current_user.id:
            flash('Unauthorized access to booking.', 'error')
            return redirect(url_for('index'))
        return render_template('confirmation.html', booking=booking)
    except Exception as e:
        logger.error(f"Error in confirmation: {str(e)}")
        flash('Error loading confirmation page.', 'error')
        return redirect(url_for('index'))

@app.route('/about')
def about():
    try:
        logger.debug(f"About route - User authenticated: {current_user.is_authenticated}")
        return render_template('about.html')
    except Exception as e:
        logger.error(f"Error loading about: {str(e)}")
        return render_template('500.html'), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        logger.debug(f"Register route called with method: {request.method}")
        if request.method == 'POST':
            logger.debug("Processing POST request for registration")
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm-password')
            
            logger.debug(f"Received form data: username={username}, email={email}")

            # Validation
            if not all([username, email, password, confirm_password]):
                error_msg = 'Please fill in all fields.'
                logger.warning(f"Validation failed: {error_msg}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('register.html')
                
            if password != confirm_password:
                error_msg = 'Passwords do not match.'
                logger.warning(f"Validation failed: {error_msg}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('register.html')
                
            logger.debug("Checking for existing username")
            if User.query.filter_by(username=username).first():
                error_msg = 'Username already exists.'
                logger.warning(f"Validation failed: {error_msg}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('register.html')
                
            logger.debug("Checking for existing email")
            if User.query.filter_by(email=email).first():
                error_msg = 'Email already registered.'
                logger.warning(f"Validation failed: {error_msg}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': error_msg}), 400
                flash(error_msg, 'error')
                return render_template('register.html')
            
            try:
                logger.debug("Generating password hash")
                hashed_password = generate_password_hash(password)
                logger.debug("Creating new user object")
                new_user = User(
                    username=username,
                    email=email,
                    password=hashed_password,
                    is_admin=False
                )
                logger.debug("Adding user to session")
                db.session.add(new_user)
                db.session.flush()
                
                logger.debug("Committing user to database")
                db.session.commit()
                logger.debug(f"User {username} created successfully with ID: {new_user.id}")
                
                logger.debug(f"Attempting to log in user {username}")
                login_success = login_user(new_user, remember=True)
                if not login_success:
                    logger.error("Failed to log in user after registration")
                    raise Exception("User login failed after registration")
                
                success_msg = 'Registration successful!'
                logger.info(f"User {username} registered and logged in successfully")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    logger.debug("Returning JSON success response")
                    return jsonify({'success': success_msg, 'redirect': url_for('index')})
                
                session.permanent = True
                flash(success_msg, 'success')
                response = make_response(redirect(url_for('index')))
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                logger.debug("Redirecting to index")
                return response
            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Database error during registration: {str(e)}")
                error_msg = 'Database error occurred. Please try again later.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': error_msg}), 500
                flash(error_msg, 'error')
                return render_template('register.html')
            except Exception as e:
                db.session.rollback()
                logger.error(f"Unexpected error during registration: {str(e)}")
                error_msg = 'Error processing registration. Please try again later.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': error_msg}), 500
                flash(error_msg, 'error')
                return render_template('register.html')
        logger.debug("Rendering register.html for GET request")
        return render_template('register.html')
    except Exception as e:
        logger.error(f"Unexpected error in register route: {str(e)}")
        error_msg = 'Error processing registration. Please try again later.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': error_msg}), 500
        flash(error_msg, 'error')
        return render_template('register.html')

@app.route('/admin')
@login_required
def admin_panel():
    try:
        logger.debug(f"Admin_panel route - User authenticated: {current_user.is_authenticated}")
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        
        # Get date filter from query parameter
        date_filter = request.args.get('date_filter')
        if date_filter:
            bookings = Booking.query.filter(Booking.date == date_filter).order_by(Booking.date.desc()).all()
        else:
            bookings = Booking.query.order_by(Booking.date.desc()).all()
        
        return render_template('admin_panel.html', 
                            menu_items=MenuItem.query.all(),
                            food_items=FoodItem.query.all(),
                            drink_items=DrinkItem.query.all(),
                            bookings=bookings,
                            messages=Contact.query.order_by(Contact.id.desc()).all())
    except Exception as e:
        logger.error(f"Error in admin_panel: {str(e)}")
        flash('Error loading admin panel. Please try again later.', 'error')
        return redirect(url_for('index'))

@app.route('/admin/add_menu_item', methods=['GET', 'POST'])
@login_required
def add_menu_item():
    try:
        logger.debug(f"Add_menu_item route - User authenticated: {current_user.is_authenticated}")
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        if request.method == 'POST':
            menu_type = request.form.get('menu_type')
            name = request.form.get('name')
            description = request.form.get('description')
            price = float(request.form.get('price'))
            category = request.form.get('category') if menu_type == 'food' else request.form.get('drink_category')
            
            if not all([menu_type, name, description, price, category]):
                flash('All fields are required.', 'error')
                return render_template('admin_menu.html')
            
            if menu_type == 'food':
                new_item = FoodItem(name=name, description=description, price=price, category=category)
            elif menu_type == 'drink':
                new_item = DrinkItem(name=name, description=description, price=price, category=category)
            else:
                flash('Invalid menu type.', 'error')
                return render_template('admin_menu.html')
            
            db.session.add(new_item)
            db.session.commit()
            flash('Menu item added successfully!', 'success')
            return redirect(url_for('admin_panel'))
        
        return render_template('admin_menu.html')
    except Exception as e:
        logger.error(f"Error in add_menu_item: {str(e)}")
        flash('Error adding menu item. Please try again later.', 'error')
        return render_template('admin_menu.html')

@app.route('/admin/delete_food_item/<int:item_id>', methods=['POST'])
@login_required
def delete_food_item(item_id):
    try:
        logger.debug(f"Delete_food_item route - User authenticated: {current_user.is_authenticated}, Item ID: {item_id}")
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        
        food_item = FoodItem.query.get_or_404(item_id)
        db.session.delete(food_item)
        db.session.commit()
        flash('Food item deleted successfully!', 'success')
        return redirect(url_for('admin_panel'))
    except Exception as e:
        logger.error(f"Error in delete_food_item: {str(e)}")
        flash('Error deleting food item. Please try again later.', 'error')
        return redirect(url_for('admin_panel'))

@app.route('/admin/delete_drink_item/<int:item_id>', methods=['POST'])
@login_required
def delete_drink_item(item_id):
    try:
        logger.debug(f"Delete_drink_item route - User authenticated: {current_user.is_authenticated}, Item ID: {item_id}")
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        
        drink_item = DrinkItem.query.get_or_404(item_id)
        db.session.delete(drink_item)
        db.session.commit()
        flash('Drink item deleted successfully!', 'success')
        return redirect(url_for('admin_panel'))
    except Exception as e:
        logger.error(f"Error in delete_drink_item: {str(e)}")
        flash('Error deleting drink item. Please try again later.', 'error')
        return redirect(url_for('admin_panel'))

@app.route('/admin/mark_message_read/<int:message_id>', methods=['POST'])
@login_required
def mark_message_read(message_id):
    try:
        logger.debug(f"Mark_message_read route - User authenticated: {current_user.is_authenticated}, Message ID: {message_id}")
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        
        message = Contact.query.get_or_404(message_id)
        message.is_read = True
        db.session.commit()
        flash('Message marked as read!', 'success')
        return redirect(url_for('admin_panel'))
    except Exception as e:
        logger.error(f"Error in mark_message_read: {str(e)}")
        flash('Error marking message as read. Please try again later.', 'error')
        return redirect(url_for('admin_panel'))

@app.route('/admin/delete_message/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    try:
        logger.debug(f"Delete_message route - User authenticated: {current_user.is_authenticated}, Message ID: {message_id}")
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('index'))
        
        message = Contact.query.get_or_404(message_id)
        db.session.delete(message)
        db.session.commit()
        flash('Message deleted successfully!', 'success')
        return redirect(url_for('admin_panel'))
    except Exception as e:
        logger.error(f"Error in delete_message: {str(e)}")
        flash('Error deleting message. Please try again later.', 'error')
        return redirect(url_for('admin_panel'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if current_user.is_authenticated:
            logger.debug(f"User {current_user.username} already logged in, redirecting to index")
            return redirect(url_for('index'))
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            if not username or not password:
                flash('Please enter username and password.', 'error')
                return render_template('login.html')
            user = User.query.filter_by(username=username).first()
            if user:
                logger.debug(f"Attempting login for {username}, stored hash: {user.password}")
                # Try sha256_crypt first (for testuser)
                if sha256_crypt.verify(password, user.password):
                    session.permanent = True
                    login_user(user, remember=True)
                    flash('Logged in successfully.', 'success')
                    logger.debug(f"User {username} logged in successfully with sha256_crypt, is_admin: {user.is_admin}")
                # Fall back to Werkzeug for regular users
                elif check_password_hash(user.password, password):
                    session.permanent = True
                    login_user(user, remember=True)
                    flash('Logged in successfully.', 'success')
                    logger.debug(f"User {username} logged in successfully with Werkzeug hash, is_admin: {user.is_admin}")
                else:
                    flash('Invalid username or password.', 'error')
                    logger.debug(f"Login failed for {username}: password mismatch")
                    return render_template('login.html')
            else:
                flash('Invalid username or password.', 'error')
                logger.debug(f"Login failed: No user found with username {username}")
                return render_template('login.html')
            
            next_page = request.args.get('next')
            if user.is_admin:
                logger.debug("Redirecting admin user to admin_panel")
                return redirect(url_for('admin_panel'))
            if next_page and urlparse(next_page).netloc == '':
                logger.debug(f"Redirecting to next_page: {next_page}")
                return redirect(next_page)
            logger.debug("Redirecting to index")
            return redirect(url_for('index'))
        return render_template('login.html')
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        flash('Error processing login. Please try again later.', 'error')
        return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    try:
        username = current_user.username if current_user.is_authenticated else "Unknown"
        logger.debug(f"Logout route - Method: {request.method}, User {username} authenticated before logout: {current_user.is_authenticated}")
        logout_user()
        session.clear()
        logger.debug(f"Session cleared - User authenticated after logout: {current_user.is_authenticated}")
        flash('Logged out successfully.', 'success')
        response = make_response(redirect(url_for('index')))
        response.delete_cookie('session')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        logger.debug(f"User {username} logged out successfully, redirecting to index")
        return response
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}")
        flash('Error logging out. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/test-connection')
def test_connection():
    try:
        logger.debug(f"Test-connection route - User authenticated: {current_user.is_authenticated}")
        result = db.session.execute(text('SELECT 1')).fetchone()
        food_count = FoodItem.query.count()
        drink_count = DrinkItem.query.count()
        return jsonify({
            'status': 'Connected',
            'database_test': bool(result),
            'food_items_count': food_count,
            'drink_items_count': drink_count
        })
    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        return jsonify({
            'status': 'Error',
            'message': str(e)
        })

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500

def get_user_bookings():
    if current_user.is_authenticated:
        return Booking.query.filter_by(user_id=current_user.id).all()
    return []

app.jinja_env.globals.update(get_user_bookings=get_user_bookings)

if __name__ == '__main__':
    with app.app_context():
        print("Setting up database...")
        try:
            db.create_all()  # Create tables without dropping
            print("✅ Database tables set up successfully!")
        except Exception as e:
            print(f"❌ Error setting up database: {str(e)}")
            db.session.rollback()
    app.run(debug=True, host='0.0.0.0', port=5000)