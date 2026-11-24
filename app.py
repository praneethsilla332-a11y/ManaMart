from flask import Flask, render_template_string, session, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "manamart_secret_key_123"

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client["manaMart"]
products = db["products"]

# Sample products
if products.count_documents({}) == 0:
    products.insert_many([
        {"name": "Tomatoes", "price": 30, "category": "Vegetables"},
        {"name": "Potatoes", "price": 25, "category": "Vegetables"},
        {"name": "Apples", "price": 120, "category": "Fruits"},
        {"name": "Milk", "price": 30, "category": "Dairy"},
        {"name": "Rice", "price": 60, "category": "Groceries"}
    ])


# HOME PAGE
@app.route("/")
def home():
    items = list(products.find())
    cart = session.get("cart", {})
    cart_count = sum(cart.values())

    return render_template_string("""
    <html>
    <head>
        <title>Mana Mart</title>
        <style>
            body {
                font-family: Arial;
                background: #f2f8f2;
                padding: 30px;
            }
            header {
                background: #168344;
                color: white;
                padding: 25px;
                text-align: center;
                border-radius: 12px;
            }
            .products {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-top: 30px;
            }
            .card {
                background: white;
                padding: 20px;
                width: 180px;
                border-radius: 12px;
                box-shadow: 0 3px 10px #ccc;
            }
            .price {
                color: green;
                font-weight: bold;
            }
            button {
                background: #168344;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 6px;
                cursor: pointer;
            }
            a {
                color: white;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>🛒 Mana Mart</h1>
            <p>Your Local Online Grocery Store</p>
            <a href="/cart">🛒 View Cart ({{ cart_count }})</a>
        </header>

        <h2>Available Products</h2>

        <div class="products">
            {% for item in items %}
            <div class="card">
                <h3>{{ item.name }}</h3>
                <p>{{ item.category }}</p>
                <p class="price">₹{{ item.price }}</p>

                <form action="/add/{{ item._id }}" method="POST">
                    <button type="submit">Add to Cart</button>
                </form>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """, items=items, cart_count=cart_count)


# ADD TO CART
@app.route("/add/<product_id>", methods=["POST"])
def add_to_cart(product_id):
    try:
        product = products.find_one({
            "_id": ObjectId(product_id)
        })

        if product:
            cart = session.get("cart", {})
            cart[product_id] = cart.get(product_id, 0) + 1
            session["cart"] = cart

    except Exception:
        pass

    return redirect(url_for("home"))


# CART PAGE
@app.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        try:
            item = products.find_one({
                "_id": ObjectId(product_id)
            })

            if item:
                subtotal = item["price"] * quantity
                total += subtotal

                cart_items.append({
                    "name": item["name"],
                    "price": item["price"],
                    "quantity": quantity,
                    "subtotal": subtotal
                })

        except Exception:
            continue

    return render_template_string("""
    <html>
    <head>
        <title>Mana Mart Cart</title>
        <style>
            body {
                font-family: Arial;
                background: #f2f8f2;
                padding: 30px;
            }
            .box {
                background: white;
                padding: 25px;
                border-radius: 12px;
            }
            a {
                color: green;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>🛒 Your Shopping Cart</h1>

            {% if cart_items %}
                {% for item in cart_items %}
                    <h3>{{ item.name }}</h3>
                    <p>Price: ₹{{ item.price }}</p>
                    <p>Quantity: {{ item.quantity }}</p>
                    <p>Subtotal: ₹{{ item.subtotal }}</p>
                    <hr>
                {% endfor %}

                <h2>Total Amount: ₹{{ total }}</h2>
            {% else %}
                <h2>Your cart is empty!</h2>
            {% endif %}

            <a href="/">← Continue Shopping</a>
        </div>
    </body>
    </html>
    """, cart_items=cart_items, total=total)


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)