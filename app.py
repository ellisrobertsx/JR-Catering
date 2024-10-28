from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, MenuItem

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
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if username in users:
            return jsonify({"error": "Username already exists"}), 400
        users[username] = {"email": email, "password": password}
        return jsonify({"message": "User registered successfully"}), 201
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]["password"] == password:
            session['username'] = username
            return jsonify({"message": "Logged in successfully"}), 200
        return jsonify({"error": "Invalid username or password"}), 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/menu')
def menu():
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
            
        # Pass menu_by_category to template as menu_items
        return render_template('menu.html', menu_items=menu_by_category)
    except Exception as e:
        print(f"Error loading menu: {str(e)}")
        return render_template('menu.html', menu_items={})  # Return empty menu if error
    finally:
        session.close()

@app.route('/menu/food')
def food_menu():
    return render_template('menu.html')

@app.route('/menu/drinks')
def drinks_menu():
    return render_template('drinks.html')

@app.route('/book')
def book():
    return render_template('book.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/admin/menu', methods=['GET', 'POST'])
def admin_menu():
    if request.method == 'POST':
        session = Session()
        try:
            new_item = MenuItem(
                name=request.form['name'],
                description=request.form['description'],
                price=float(request.form['price']),
                category=request.form['category']
            )
            session.add(new_item)
            session.commit()
            return jsonify({"message": "Menu item added successfully"}), 201
        finally:
            session.close()
    return render_template('admin_menu.html')

if __name__ == '__main__':
    test_db_connection()  # Test database connection before starting the app
    app.run(debug=True)
