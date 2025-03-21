from app import app, db, DrinkItem, FoodItem

def init_db():
    with app.app_context():
        print("Starting database initialization...")
        
        
        db.create_all()
        print("Tables created successfully")
        
        # Clear existing data
        DrinkItem.query.delete()
        FoodItem.query.delete()
        print("Cleared existing items")
        
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
            
            foods = [
                FoodItem(
                    name='Garlic Bread',
                    description='Fresh baked bread with garlic butter',
                    price=4.99,
                    category='Starters'
                ),
                FoodItem(
                    name='Caesar Salad',
                    description='Crisp romaine lettuce, parmesan, croutons, and Caesar dressing',
                    price=9.99,
                    category='Starters'
                ),
                FoodItem(
                    name='Classic Burger',
                    description='6oz beef patty with lettuce, tomato, and our special sauce',
                    price=12.99,
                    category='Mains'
                ),
                FoodItem(
                    name='Fish & Chips',
                    description='Beer-battered cod with hand-cut chips and mushy peas',
                    price=14.99,
                    category='Mains'
                ),
                FoodItem(
                    name='Chocolate Brownie',
                    description='Warm chocolate brownie with vanilla ice cream',
                    price=6.99,
                    category='Desserts'
                ),
                FoodItem(
                    name='Sticky Toffee Pudding',
                    description='Classic dessert with butterscotch sauce',
                    price=6.99,
                    category='Desserts'
                )
            ]
            
            for drink in drinks:
                db.session.add(drink)
            for food in foods:
                db.session.add(food)

            db.session.commit()
            print("Successfully committed all changes")
            
            all_drinks = DrinkItem.query.all()
            all_foods = FoodItem.query.all()
            print(f"\nVerification: Found {len(all_drinks)} drinks and {len(all_foods)} food items in database")
                
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    init_db()
