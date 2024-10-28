from app import engine, Session, MenuItem, DrinkItem, User, Booking, Base
from werkzeug.security import generate_password_hash

def init_db():
    # Drop existing tables and recreate them
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    session = Session()
    
    try:
        # Add a test admin user
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('Admin123!'),
            is_admin=True
        )
        
        session.add(admin_user)
        
        # Sample menu items
        items = [
            MenuItem(
                name="Garlic Bread",
                description="Fresh bread with garlic butter",
                price=4.99,
                category="Starters"
            ),
            MenuItem(
                name="Haggis Bon Bons",
                description="A classic haggis with all the trimmings",
                price=6.99,
                category="Starters"
            ),
            MenuItem(
                name="Prawn Cocktail",
                description="Prawns in a classic cocktail sauce",
                price=7.99,
                category="Starters"
            ),
            MenuItem(
                name="Fish and Chips",
                description="Fish and Chips with hand-cut chips",
                price=14.99,
                category="Main Course"
            ),
            MenuItem(
                name="Steak Pie",
                description="Steak pie with mashed potatoes and vegetables",
                price=14.99,
                category="Main Course"
            ),
            MenuItem(
                name="Lasagna",
                description="Lasagna with marinara sauce",
                price=14.99,
                category="Main Course"
            ),
            MenuItem(
                name="Chocolate Cake",
                description="Rich chocolate cake with cream",
                price=5.99,
                category="Desserts"
            ),
            MenuItem(
                name="Cheesecake",
                description="Cheesecake with strawberry sauce",
                price=5.99,
                category="Desserts"
            ),
            MenuItem(
                name="Apple Crumble",
                description="Apple crumble with custard",
                price=5.99,
                category="Desserts"
            )
        ]

        # Sample drink items
        drink_items = [
            DrinkItem(
                name="House Red Wine",
                description="Smooth medium-bodied red wine",
                price=5.99,
                category="Wine"
            ),
            DrinkItem(
                name="House White Wine",
                description="Crisp and refreshing white wine",
                price=5.99,
                category="Wine"
            ),
            DrinkItem(
                name="Prosecco",
                description="A sparkling white wine with crisp apple and pear notes",
                price=5.99,
                category="Wine"
            ),
            DrinkItem(
                name="Guinness",
                description="Irish dry stout with a creamy texture",
                price=5.99,
                category="Beer"
            ),
            DrinkItem(
                name="Carlsberg",
                description="Danish pilsner with a balanced hop and malt profile",
                price=5.99,
                category="Beer"
            ),
            DrinkItem(
                name="Heineken",
                description="Dutch pale lager with a crisp taste",
                price=5.99,
                category="Beer"
            ),
            DrinkItem(
                name="Margarita",
                description="Classic Margarita with salt and lime",
                price=7.99,
                category="Cocktails"
            ),
            DrinkItem(
                name="Mojito",
                description="Classic Mojito with mint and lime",
                price=7.99,
                category="Cocktails"
            ),
            DrinkItem(
                name="Negroni",
                description="Classic Negroni with gin, vermouth, and bitters",
                price=7.99,
                category="Cocktails"
            )
        ]
        
        # Add all items to the session
        session.add_all(items)
        session.add_all(drink_items)
        session.commit()
        
        print("Added sample menu items successfully!")
        
        # Verify items were added
        all_items = session.query(MenuItem).all()
        all_drinks = session.query(DrinkItem).all()
        
        print(f"\nVerifying added food items:")
        for item in all_items:
            print(f"- {item.name} ({item.category})")
            
        print(f"\nVerifying added drink items:")
        for item in all_drinks:
            print(f"- {item.name} ({item.category})")
            
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_db()
