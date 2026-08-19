from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import engine, SessionLocal, Base
from models import MenuItem, Order


Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# REQUEST MODELS
# -------------------------

class FoodItem(BaseModel):
    name: str
    price: int
    category: str


class OrderItem(BaseModel):
    item_name: str
    quantity: int
    total_price: int


class OrderStatus(BaseModel):
    status: str


# -------------------------
# FOOD IMAGES
# -------------------------

FOOD_IMAGES = {
    "Burger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80",

    "Pizza": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=800&q=80",

    "Biryani": "https://images.unsplash.com/photo-1563379091339-03246963d96c?auto=format&fit=crop&w=800&q=80",

    "Fried Rice": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=800&q=80",

    "Noodles": "https://images.unsplash.com/photo-1557872943-16a5ac26437e?auto=format&fit=crop&w=800&q=80",

    "Dosa": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?auto=format&fit=crop&w=800&q=80",

    "Idli": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=800&q=80",

    "Chicken": "https://images.unsplash.com/photo-1598103442097-8b74394b95c6?auto=format&fit=crop&w=800&q=80",

    "Paneer": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=800&q=80",

    "French Fries": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=800&q=80"
}


# -------------------------
# GET FOOD IMAGE
# -------------------------

def get_food_image(food_name):

    if food_name in FOOD_IMAGES:
        return FOOD_IMAGES[food_name]

    return (
        "https://images.unsplash.com/"
        "photo-1546069901-ba9599a7e63c"
        "?auto=format&fit=crop&w=800&q=80"
    )


# -------------------------
# HOME
# -------------------------

@app.get("/")
def home():

    return {
        "message": "QR Menu Backend is working!",
        "status": "success"
    }


# -------------------------
# MENU
# -------------------------

@app.get("/menu")
def get_menu():

    db: Session = SessionLocal()

    items = db.query(MenuItem).all()

    result = []

    for item in items:

        result.append({
            "id": item.id,
            "name": item.name,
            "price": item.price,
            "category": item.category,
            "image": get_food_image(item.name)
        })

    db.close()

    return {
        "restaurant": "Lassi Day Cafe",
        "items": result
    }


@app.post("/menu")
def add_food(food: FoodItem):

    db: Session = SessionLocal()

    new_item = MenuItem(
        name=food.name,
        price=food.price,
        category=food.category
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    db.close()

    return {
        "message": "Food item added successfully!",
        "item": {
            "id": new_item.id,
            "name": new_item.name,
            "price": new_item.price,
            "category": new_item.category,
            "image": get_food_image(new_item.name)
        }
    }


# -------------------------
# CREATE ORDER
# -------------------------

@app.post("/orders")
def create_order(order: OrderItem):

    db: Session = SessionLocal()

    new_order = Order(
        item_name=order.item_name,
        quantity=order.quantity,
        total_price=order.total_price
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    result = {
        "id": new_order.id,
        "item_name": new_order.item_name,
        "quantity": new_order.quantity,
        "total_price": new_order.total_price,
        "status": new_order.status
    }

    db.close()

    return {
        "message": "Order placed successfully!",
        "order": result
    }


# -------------------------
# GET ALL ORDERS
# -------------------------

@app.get("/orders")
def get_orders():

    db: Session = SessionLocal()

    orders = db.query(Order).all()

    result = []

    for order in orders:

        result.append({
            "id": order.id,
            "item_name": order.item_name,
            "quantity": order.quantity,
            "total_price": order.total_price,
            "status": order.status
        })

    db.close()

    return {
        "orders": result
    }


# -------------------------
# UPDATE ORDER STATUS
# -------------------------

@app.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status_data: OrderStatus
):

    db: Session = SessionLocal()

    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:

        db.close()

        return {
            "message": "Order not found"
        }

    allowed_statuses = [
        "Pending",
        "Preparing",
        "Ready",
        "Completed"
    ]

    if status_data.status not in allowed_statuses:

        db.close()

        return {
            "message": "Invalid status",
            "allowed_statuses": allowed_statuses
        }

    order.status = status_data.status

    db.commit()
    db.refresh(order)

    result = {
        "id": order.id,
        "item_name": order.item_name,
        "quantity": order.quantity,
        "total_price": order.total_price,
        "status": order.status
    }

    db.close()

    return {
        "message": "Order status updated successfully!",
        "order": result
    }