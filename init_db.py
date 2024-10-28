from app import engine, Session, MenuItem, Base

def init_db():
    # Create tables
    Base.metadata.create_all(engine)
    
    session = Session()
    
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
            name="Chocolate Cake",
            description="Rich chocolate cake with cream",
            price=5.99,
            category="Desserts"
        )
    ]
    
    try:
        session.add_all(items)
        session.commit()
        print("Added sample menu items successfully!")
    except Exception as e:
        print(f"Error adding menu items: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_db()
