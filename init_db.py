from app import app, db
from models import User, MenuItem, DrinkItem
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Clear existing data
        DrinkItem.query.delete()
        MenuItem.query.delete()
        
        try:
            # Add drink items
            drinks = [
                DrinkItem(
                    name='House Red Wine',
                    description='Smooth medium-bodied red wine',
                    price=5.99,
                    category='Wine'
                ),
                DrinkItem(
                    name='House White Wine',
                    description='Crisp and refreshing white wine',
                    price=5.99,
                    category='Wine'
                ),
                DrinkItem(
                    name='Prosecco',
                    description='Light and bubbly Italian sparkling wine',
                    price=6.99,
                    category='Wine'
                ),
                DrinkItem(
                    name='Draft Beer',
                    description='Local craft beer on tap',
                    price=4.99,
                    category='Beer'
                ),
                DrinkItem(
                    name='Bottled Beer',
                    description='Selection of premium bottled beers',
                    price=3.99,
                    category='Beer'
                ),
                DrinkItem(
                    name='Mojito',
                    description='Rum, lime, mint, and soda water',
                    price=7.99,
                    category='Cocktails'
                ),
                DrinkItem(
                    name='Margarita',
                    description='Tequila, triple sec, and lime juice',
                    price=7.99,
                    category='Cocktails'
                ),
                DrinkItem(
                    name='Gin & Tonic',
                    description='Premium gin with tonic water and lime',
                    price=6.99,
                    category='Cocktails'
                )
            ]

            # Add all drinks to the session
            for drink in drinks:
                db.session.add(drink)

            # Commit the changes
            db.session.commit()
            print("Database initialized successfully!")
            
            # Verify the data was added
            all_drinks = DrinkItem.query.all()
            print("\nVerifying added drinks:")
            for drink in all_drinks:
                print(f"- {drink.name} ({drink.category}): £{drink.price}")
                
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    init_db()
