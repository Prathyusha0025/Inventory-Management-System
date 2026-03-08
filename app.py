from flask import Flask, render_template, request, jsonify
from database import db
from models import Product
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:password@localhost/inventory_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Home Page
@app.route("/")
def home():
    products = Product.query.all()
    return render_template("index.html", products=products)

# Add Product
@app.route("/add", methods=["POST"])
def add_product():
    name = request.form["name"]
    quantity = int(request.form["quantity"])
    reorder_level = int(request.form["reorder"])

    product = Product(
        name=name,
        quantity=quantity,
        reorder_level=reorder_level
    )

    db.session.add(product)
    db.session.commit()

    return "Product Added"

# REST API - Get Products
@app.route("/api/products")
def get_products():
    products = Product.query.all()

    data = []
    for p in products:
        data.append({
            "id": p.id,
            "name": p.name,
            "quantity": p.quantity,
            "reorder_level": p.reorder_level
        })

    return jsonify(data)

# REST API - Update Stock
@app.route("/api/update/<int:id>", methods=["PUT"])
def update_stock(id):

    product = Product.query.get(id)
    data = request.json

    product.quantity = data["quantity"]
    db.session.commit()

    return jsonify({"message": "Stock Updated"})


# Low Stock Alert
@app.route("/low-stock")
def low_stock():

    products = Product.query.all()

    low_items = []

    for p in products:
        if p.quantity <= p.reorder_level:
            low_items.append(p.name)

    return jsonify({
        "low_stock_products": low_items
    })

# Matplotlib Chart
@app.route("/chart")
def chart():

    products = Product.query.all()

    names = [p.name for p in products]
    quantities = [p.quantity for p in products]

    plt.figure()

    plt.bar(names, quantities)

    plt.title("Inventory Stock Levels")
    plt.xlabel("Products")
    plt.ylabel("Quantity")

    if not os.path.exists("static"):
        os.makedirs("static")

    path = "static/chart.png"
    plt.savefig(path)

    return render_template("chart.html", chart=path)


if __name__ == "__main__":
    app.run(debug=True)
