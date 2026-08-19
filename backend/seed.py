from database import SessionLocal, engine, Base
from models import MenuItem

# Make sure the database table exists
Base.metadata.create_all(bind=engine)

db = SessionLocal()

items = [
    MenuItem(name="Burger", price=120, category="Main Course"),
    MenuItem(name="Pizza", price=200, category="Main Course"),
    MenuItem(name="French Fries", price=80, category="Starters"),
]

db.add_all(items)
db.commit()
db.close()

print("Menu items added successfully!")