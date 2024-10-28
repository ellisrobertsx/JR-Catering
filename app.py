from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, MenuItem, DrinkItem, User, Booking
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# Dummy user data (replace this with a database later)
users = {}

# Connection URL format: postgresql://username:password@host:port/database_name
DATABASE_URL = "postgresql://postgres:Burngask10!@localhost:5432/JR-CATERING"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def test_db_connection():
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            # Basic connection test
            result = connection.execute(text("SELECT 1"))
            print("\n=== Database Connection Test ===")
            print("✓ Basic connection test passed!")
            
            # Get PostgreSQL version
            version = connection.execute(text("SELECT version()"))
            print(f"✓ Connected to: {version.scalar()}")
            
            # Add this new test to check database name
            current_db = connection.execute(text("SELECT current_database()"))
            db_name = current_db.scalar()
            print(f"✓ Connected to database: {db_name}")
            
            print("==============================\n")
            return True
            
    except Exception as e:
        print("\n=== Database Connection Error ===")
        print(f"❌ Connection failed: {str(e)}")
        print("==============================\n")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db_session = Session()
        try:
            # Get form data
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            # Check if username or email already exists
            existing_user = db_session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                return jsonify({
                    "error": "Username or email already exists"
                }), 400
            
            # Create new user with hashed password
            new_user = User(
                username=username,
                email=email,
                password=generate_password_hash(password, method='pbkdf2:sha256')
            )
            
            db_session.add(new_user)
            db_session.commit()
            return jsonify({"message": "User registered successfully"}), 201
            
        except Exception as e:
            db_session.rollback()
            print(f"Registration error: {str(e)}")
            return jsonify({"error": "Registration failed"}), 500
        finally:
            db_session.close()
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("\n=== Login Route Accessed ===")  # Debug print
    
    if request.method == 'POST':
        print("POST request received")  # Debug print
        db_session = Session()
        
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Login attempt for username: {username}")  # Debug print
        
        try:
            user = db_session.query(User).filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):
                print("Login successful!")  # Debug print
                session['username'] = user.username
                session['user_id'] = user.id
                session['is_admin'] = user.is_admin
                db_session.close()
                print("Redirecting to index...")  # Debug print
                return redirect('/')  # Direct redirect to home page
            
            print("Login failed - invalid credentials")  # Debug print
            
        except Exception as e:
            print(f"Database error: {str(e)}")  # Debug print
        finally:
            db_session.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/menu')
def menu():
    session = Session()
    try:
        # Query all menu items from database
        menu_items = session.query(MenuItem).all()
        
        # Debug print
        print("\nDebug: Found menu items:")
        for item in menu_items:
            print(f"- {item.name} ({item.category})")
        
        # Initialize categories dictionary
        menu_by_category = {
            'Starters': [],
            'Main Course': [],
            'Desserts': []
        }
        
        # Sort items into categories
        for item in menu_items:
            if item.category in menu_by_category:
                menu_by_category[item.category].append(item)
            
        # Debug print
        print("\nDebug: Categorized items:")
        for category, items in menu_by_category.items():
            print(f"{category}: {len(items)} items")
            
        return render_template('menu.html', menu_items=menu_by_category)
    except Exception as e:
        print(f"Error loading menu: {str(e)}")
        return render_template('menu.html', menu_items={})
    finally:
        session.close()

@app.route('/menu/food')
def food_menu():
    session = Session()
    try:
        # Query all menu items from database
        menu_items = session.query(MenuItem).all()
        
        # Initialize categories dictionary
        menu_by_category = {
            'Starters': [],
            'Main Course': [],
            'Desserts': []
        }
        
        # Sort items into categories
        for item in menu_items:
            if item.category in menu_by_category:
                menu_by_category[item.category].append(item)
        
        # Debug print
        print("Found menu items:", len(menu_items))
        for category, items in menu_by_category.items():
            print(f"{category}: {len(items)} items")
            
        return render_template('menu.html', menu_items=menu_by_category)
    except Exception as e:
        print(f"Error loading food menu: {str(e)}")
        return render_template('menu.html', menu_items={})
    finally:
        session.close()

@app.route('/menu/drinks')
def drinks_menu():
    session = Session()
    try:
        # Query all drink items from database
        drink_items = session.query(DrinkItem).all()
        
        # Initialize categories dictionary
        menu_by_category = {
            'Wine': [],
            'Beer': [],
            'Cocktails': []
        }
        
        # Sort items into categories
        for item in drink_items:
            if item.category in menu_by_category:
                menu_by_category[item.category].append(item)
        
        # Debug print
        print("Found drink items:", len(drink_items))
        for category, items in menu_by_category.items():
            print(f"{category}: {len(items)} items")
            
        return render_template('drinks.html', menu_items=menu_by_category)
    except Exception as e:
        print(f"Error loading drinks menu: {str(e)}")
        return render_template('drinks.html', menu_items={})
    finally:
        session.close()

@app.route('/book', methods=['GET', 'POST'])
def book():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to make or view bookings.', 'error')
        return redirect(url_for('login'))
    
    db_session = Session()
    
    try:
        if request.method == 'POST':
            # Get form data
            date = request.form['date']
            time = request.form['time']
            
            # Validate date and time
            booking_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            current_datetime = datetime.now()
            
            if booking_datetime < current_datetime:
                flash('Cannot book a table in the past. Please select a future date and time.', 'error')
                return redirect(url_for('book'))
            
            # Create new booking with user_id
            new_booking = Booking(
                name=request.form['name'],
                email=request.form['email'],
                phone=request.form['phone'],
                date=date,
                time=time,
                guests=int(request.form['guests']),
                special_requests=request.form.get('special-requests', ''),
                user_id=session['user_id']  # Add the user_id from session
            )
            
            db_session.add(new_booking)
            db_session.commit()
            flash('Booking created successfully!', 'success')
            return redirect(url_for('book'))
                
        # Get only the logged-in user's bookings
        bookings = db_session.query(Booking).filter_by(user_id=session['user_id']).order_by(Booking.date, Booking.time).all()
        return render_template('book.html', bookings=bookings)
            
    except Exception as e:
        db_session.rollback()
        print(f"Booking error: {str(e)}")
        flash('Error processing booking request. Please try again.', 'error')
        return render_template('book.html', bookings=[])
    finally:
        db_session.close()

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/admin/menu', methods=['GET', 'POST'])
def admin_menu():
    if request.method == 'POST':
        session = Session()
        try:
            menu_type = request.form['menu_type']
            if menu_type == 'food':
                new_item = MenuItem(
                    name=request.form['name'],
                    description=request.form['description'],
                    price=float(request.form['price']),
                    category=request.form['category']
                )
            else:  # drink
                new_item = DrinkItem(
                    name=request.form['name'],
                    description=request.form['description'],
                    price=float(request.form['price']),
                    category=request.form['drink_category']
                )
            session.add(new_item)
            session.commit()
            return jsonify({"message": "Item added successfully"}), 201
        finally:
            session.close()
    return render_template('admin_menu.html')

@app.route('/booking/<int:booking_id>/edit', methods=['POST'])
def edit_booking(booking_id):
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Please log in to edit bookings.'})
    
    db_session = Session()
    try:
        booking = db_session.query(Booking).get(booking_id)
        
        # Check if booking exists and belongs to the logged-in user
        if not booking or booking.user_id != session['user_id']:
            flash('Booking not found or unauthorized.', 'error')
            return redirect(url_for('book'))
        
        # Validate date and time
        date = request.form['date']
        time = request.form['time']
        booking_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        current_datetime = datetime.now()
        
        if booking_datetime < current_datetime:
            flash('Cannot update booking to a past date/time.', 'error')
            return redirect(url_for('book'))
            
        booking.date = date
        booking.time = time
        booking.guests = int(request.form['guests'])
        booking.special_requests = request.form.get('special-requests', '')
        
        db_session.commit()
        flash('Booking updated successfully!', 'success')
        return redirect(url_for('book'))
            
    except Exception as e:
        db_session.rollback()
        flash('Error updating booking. Please try again.', 'error')
        return redirect(url_for('book'))
    finally:
        db_session.close()

@app.route('/booking/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Please log in to cancel bookings.'})
    
    db_session = Session()
    try:
        booking = db_session.query(Booking).get(booking_id)
        
        # Check if booking exists and belongs to the logged-in user
        if not booking or booking.user_id != session['user_id']:
            return jsonify({'success': False, 'error': 'Booking not found or unauthorized'})
        
        db_session.delete(booking)
        db_session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db_session.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        db_session.close()

if __name__ == '__main__':
    test_db_connection()  # Test database connection before starting the app
    app.run(debug=True)
