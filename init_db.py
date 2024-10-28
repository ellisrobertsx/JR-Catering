from app import engine, Session, MenuItem, DrinkItem, User, Base
from werkzeug.security import generate_password_hash

def init_db():
    # Drop existing tables and recreate them
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    session = Session()
    
    # Add a test admin user
    admin_user = User(
        username='admin',
        email='admin@example.com',
        password=generate_password_hash('Admin123!'),
        is_admin=True
    )
    
    try:
        session.add(admin_user)
        
        # Check if we already have menu items
        existing_items = session.query(MenuItem).first()
        if existing_items:
            print("Database already has menu items!")
            return
        
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
                name="Crab Cakes",
                description="Crab cakes with a classic tartar sauce",
                price=8.99,
                category="Starters"
            ),
            MenuItem(
                name="Scallops",
                description="Scallops with a classic lemon butter sauce",
                price=10.99,
                category="Starters"
            ),
            MenuItem(
                name="Caesar Salad",
                description="Classic Caesar salad with croutons",
                price=6.99,
                category="Starters"
            ),
            MenuItem(
                name="Steak and Chips",
                description="8oz sirloin steak with hand-cut chips",
                price=19.99,
                category="Main Course"
            ),
            MenuItem(
                name="Chicken Tikka Masala",
                description="Chicken Tikka Masala with rice and naan bread",
                price=14.99,
                category="Main Course"
            ),
            MenuItem(
                name="Beef Wellington",
                description="Beef Wellington with mashed potatoes and vegetables",
                price=24.99,
                category="Main Course"
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
            ),
            MenuItem(
                name="Banana Bread",
                description="Banana bread with cream cheese frosting",
                price=5.99,
                category="Desserts"
            ),
            MenuItem(
                name="Chocolate Chip Cookies",
                description="Chocolate chip cookies with milk",
                price=5.99,
                category="Desserts"
            )
        ]

        drink_items = [
            DrinkItem(
                name="House Red Wine",
                description="Smooth medium-bodied red wine",
                price=5.99,
                category="Wine"
            ),
            DrinkItem(
                name="Draft Beer",
                description="Local craft beer",
                price=4.99,
                category="Beer"
            ),
            DrinkItem(
                name="House White Wine",
                description="Smooth medium-bodied white wine",
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
                name="Cava",
                description="A Spanish sparkling wine with citrus and almond flavors",
                price=5.99,
                category="Wine"
            ),
            DrinkItem(
                name="Guinness",
                description="Irish dry stout with a creamy texture and roasted flavor",
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
                description="Dutch pale lager with a crisp and slightly bitter taste",
                price=5.99,
                category="Beer"
            ),
            DrinkItem(
                name="Fosters",
                description="Australian lager with a crisp and slightly bitter taste",
                price=5.99,
                category="Beer"
            ),  
            DrinkItem(
                name="Tennents",
                description="Scottish pale lager with a crisp and slightly bitter taste",
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
            ),
            DrinkItem(
                name="Cosmopolitan",
                description="Classic Cosmopolitan with vodka, cranberry, lime, and orange",
                price=7.99,
                category="Cocktails"
            ),
            
        ]
        
        try:
            session.add_all(items)
            session.add_all(drink_items)
            session.commit()
            print("Added sample menu items successfully!")
            
            # Add this to verify items were added
            all_items = session.query(MenuItem).all()
            all_drinks = session.query(DrinkItem).all()
            
            print(f"\nVerifying added items:")
            for item in all_items:
                print(f"- {item.name} ({item.category})")
                
            print(f"\nVerifying added drink items:")
            for item in all_drinks:
                print(f"- {item.name} ({item.category})")
                
        except Exception as e:
            print(f"Error adding menu items: {str(e)}")
            session.rollback()
        finally:
            session.close()

if __name__ == "__main__":
    init_db()
