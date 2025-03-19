from app import app, db  # Import app and db from app.py
from models import User, MenuItem, DrinkItem  # Import models from models.py

def check_database():
    with app.app_context():  # Set up application context
        session = db.session
        try:
            # Check Users
            print("\n=== Users in Database ===")
            users = session.query(User).all()
            for user in users:
                print(f"Username: {user.username}")
                print(f"Email: {user.email}")
                print(f"Is Admin: {user.is_admin}")
                print("---")
            
            # Check Menu Items
            print("\n=== Food Menu Items ===")
            menu_items = session.query(MenuItem).all()
            for item in menu_items:
                print(f"Name: {item.name}")
                print(f"Category: {item.category}")
                print(f"Price: £{item.price}")
                print("---")
            
            # Check Drink Items
            print("\n=== Drink Menu Items ===")
            drink_items = session.query(DrinkItem).all()
            for drink in drink_items:
                print(f"Name: {drink.name}")
                print(f"Category: {drink.category}")
                print(f"Price: £{drink.price}")
                print("---")
                
        except Exception as e:
            print(f"Error checking database: {str(e)}")
        finally:
            session.close()

if __name__ == "__main__":
    check_database()