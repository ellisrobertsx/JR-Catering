from flask import Flask, request, jsonify, g
from database import Session, User, MenuItem, Booking, ContactMessage, Category
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()  # This loads the variables from .env

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

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        new_user = User(username=data['username'], email=data['email'])
        new_user.set_password(data['password'])
        g.session.add(new_user)
        g.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except SQLAlchemyError as e:
        g.session.rollback()
        return jsonify({"message": "Registration failed", "error": str(e)}), 400

@app.route('/login', methods=['POST'])
def login():
    auth = request.json
    user = g.session.query(User).filter_by(username=auth['username']).first()
    if not user or not user.check_password(auth['password']):
        return jsonify({"message": "Invalid username or password"}), 401
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config['SECRET_KEY'])
    return jsonify({'token': token})

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
        user_count = g.session.query(User).count()
        return jsonify({"message": f"Database connected successfully. User count: {user_count}"}), 200
    except Exception as e:
        return jsonify({"message": f"Database connection failed: {str(e)}"}), 500

@app.errorhandler(Exception)
def handle_error(error):
    message = str(error)
    status_code = 500
    if hasattr(error, 'code'):
        status_code = error.code
    return jsonify({"message": message}), status_code

if __name__ == '__main__':
    app.run(debug=True)
