from flask import Flask, request, jsonify, g, render_template, redirect, url_for
from database import Session, User, MenuItem, Booking, ContactMessage, Category
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()  # This loads the variables from .env

from flask import Flask, request, jsonify, g, render_template, redirect, url_for
from database import Session, User, MenuItem, Booking, ContactMessage, Category
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Session().query(User).filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.before_request
def create_session():
    g.session = Session()

@app.teardown_appcontext
def shutdown_session(exception=None):
    session = g.pop('session', None)
    if session is not None:
        session.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        # Handle booking form submission
        # Add your booking logic here
        return jsonify({"message": "Booking submitted successfully"}), 201
    else:
        return render_template('book.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle contact form submission
        # Add your contact form logic here
        return jsonify({"message": "Message sent successfully"}), 201
    else:
        return render_template('contact.html')

@app.route('/drinks')
def drinks():
    return render_template('drinks.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        auth = request.json
        user = g.session.query(User).filter_by(username=auth['username']).first()
        if not user or not user.check_password(auth['password']):
            return jsonify({"message": "Invalid username or password"}), 401
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    else:
        return render_template('login.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle registration form submission
        # Add your registration logic here
        return jsonify({"message": "User registered successfully"}), 201
    else:
        return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = Session().query(User).filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.before_request
def create_session():
    g.session = Session()

@app.teardown_appcontext
def shutdown_session(exception=None):
    session = g.pop('session', None)
    if session is not None:
        session.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        # Handle POST request (form submission)
        # Add your booking logic here
        # For example:
        # new_booking = Booking(
        #     user_id=current_user.id,
        #     date=request.form['date'],
        #     time=request.form['time'],
        #     guests=request.form['guests'],
        #     special_requests=request.form['special-requests']
        # )
        # g.session.add(new_booking)
        # g.session.commit()
        # return jsonify({"message": "Booking successful"}), 201
        pass
    else:
        # Handle GET request (display booking form)
        return render_template('book.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/drinks')
def drinks():
    return render_template('drinks.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        auth = request.json
        user = g.session.query(User).filter_by(username=auth['username']).first()
        if not user or not user.check_password(auth['password']):
            return jsonify({"message": "Invalid username or password"}), 401
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    else:
        return render_template('login.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/book', methods=['POST'])
@token_required
def book(current_user):
    data = request.json
    try:
        new_booking = Booking(
            user_id=current_user.id,
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            date=data['date'],
            time=data['time'],
            guests=data['guests'],
            special_requests=data.get('special_requests')
        )
        g.session.add(new_booking)
        g.session.commit()
        return jsonify({"message": "Booking created successfully"}), 201
    except SQLAlchemyError as e:
        g.session.rollback()
        return jsonify({"message": "Booking failed", "error": str(e)}), 400

@app.route('/menu', methods=['GET'])
def get_menu():
    menu_items = g.session.query(MenuItem).all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'price': item.price,
        'category': item.category.name
    } for item in menu_items])

@app.route('/contact', methods=['POST'])
def contact():
    data = request.json
    try:
        new_message = ContactMessage(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            message=data['message']
        )
        g.session.add(new_message)
        g.session.commit()
        return jsonify({"message": "Message sent successfully"}), 201
    except SQLAlchemyError as e:
        g.session.rollback()
        return jsonify({"message": "Message sending failed", "error": str(e)}), 400

@app.route('/test_db')
def test_db():
    try:
        # Test connection
        g.session.execute("SELECT 1")
        
        # Count entities
        user_count = g.session.query(User).count()
        menu_item_count = g.session.query(MenuItem).count()
        booking_count = g.session.query(Booking).count()
        category_count = g.session.query(Category).count()
        contact_message_count = g.session.query(ContactMessage).count()
        
        return jsonify({
            "message": "Database connected successfully",
            "user_count": user_count,
            "menu_item_count": menu_item_count,
            "booking_count": booking_count,
            "category_count": category_count,
            "contact_message_count": contact_message_count
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            "message": "Database error",
            "error": str(e),
            "error_type": type(e).__name__
        }), 500
    except Exception as e:
        return jsonify({
            "message": "Unexpected error",
            "error": str(e),
            "error_type": type(e).__name__
        }), 500

@app.route('/add_test_data')
def add_test_data():
    try:
        # Add a test user
        test_user = User(username="testuser", email="test@example.com")
        test_user.set_password("testpassword")
        g.session.add(test_user)

        # Add a test category
        test_category = Category(name="Test Category")
        g.session.add(test_category)
        g.session.flush()  # This assigns an ID to test_category

        # Add a test menu item
        test_menu_item = MenuItem(
            name="Test Item",
            description="A test menu item",
            price=9.99,
            category_id=test_category.id
        )
        g.session.add(test_menu_item)

        # Add a test booking
        test_booking = Booking(
            user_id=test_user.id,
            name="Test Booking",
            email="booking@example.com",
            phone="1234567890",
            date=datetime.now().date(),
            time=datetime.now().time(),
            guests=2
        )
        g.session.add(test_booking)

        # Add a test contact message
        test_message = ContactMessage(
            name="Test Contact",
            email="contact@example.com",
            phone="0987654321",
            message="This is a test message"
        )
        g.session.add(test_message)

        g.session.commit()
        return jsonify({"message": "Test data added successfully"}), 201
    except SQLAlchemyError as e:
        g.session.rollback()
        return jsonify({
            "message": "Error adding test data",
            "error": str(e),
            "error_type": type(e).__name__
        }), 500

@app.errorhandler(Exception)
def handle_error(error):
    message = str(error)
    status_code = 500
    if hasattr(error, 'code'):
        status_code = error.code
    return jsonify({"message": message}), status_code

if __name__ == '__main__':
    app.run(debug=True)
