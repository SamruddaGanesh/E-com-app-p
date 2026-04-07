from datetime import datetime
from functools import wraps

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key-change-me"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ecommerce.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    user = db.relationship("User", backref=db.backref("cart_items", lazy=True))
    product = db.relationship("Product")


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("orders", lazy=True))


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    order = db.relationship("Order", backref=db.backref("items", lazy=True, cascade="all, delete-orphan"))


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        if not g.user.is_admin:
            flash("Admin access required.", "error")
            return redirect(url_for("index"))
        return view(*args, **kwargs)

    return wrapped


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)


@app.context_processor
def inject_user():
    return {"current_user": g.user}


def ensure_admin_user() -> None:
    admin = User.query.filter_by(username="admin").first()
    if admin is None:
        admin = User(
            username="admin",
            password_hash=generate_password_hash("admin123"),
            is_admin=True,
        )
        db.session.add(admin)
        db.session.commit()


def seed_products() -> None:
    if Product.query.count() == 0:
        initial_products = [
            Product(name="Laptop", price=70000, stock=8),
            Product(name="Keyboard", price=1200, stock=25),
            Product(name="Mouse", price=600, stock=30),
            Product(name="Headphones", price=2400, stock=15),
        ]
        db.session.add_all(initial_products)
        db.session.commit()


def init_db() -> None:
    db.create_all()
    ensure_admin_user()
    seed_products()


@app.route("/")
@login_required
def index():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template("index.html", products=products)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("register.html")

        if User.query.filter_by(username=username).first() is not None:
            flash("Username already exists.", "error")
            return render_template("register.html")

        user = User(username=username, password_hash=generate_password_hash(password), is_admin=False)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user is None or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials.", "error")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user.id
        flash("Logged in successfully.", "success")
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/add-to-cart/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id: int):
    quantity = request.form.get("quantity", "1")
    try:
        quantity_int = int(quantity)
    except ValueError:
        flash("Quantity must be a number.", "error")
        return redirect(url_for("index"))

    if quantity_int <= 0:
        flash("Quantity must be at least 1.", "error")
        return redirect(url_for("index"))

    product = Product.query.get_or_404(product_id)
    if product.stock <= 0:
        flash("This item is out of stock.", "error")
        return redirect(url_for("index"))

    existing_item = CartItem.query.filter_by(user_id=g.user.id, product_id=product_id).first()
    existing_qty = existing_item.quantity if existing_item else 0

    if existing_qty + quantity_int > product.stock:
        flash(f"Only {product.stock} item(s) available in stock.", "error")
        return redirect(url_for("index"))

    if existing_item:
        existing_item.quantity += quantity_int
    else:
        db.session.add(CartItem(user_id=g.user.id, product_id=product_id, quantity=quantity_int))

    db.session.commit()
    flash("Item added to cart.", "success")
    return redirect(url_for("index"))


@app.route("/cart")
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=g.user.id).all()
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    return render_template("cart.html", cart_items=cart_items, subtotal=subtotal)


@app.route("/cart/update/<int:item_id>", methods=["POST"])
@login_required
def update_cart(item_id: int):
    item = CartItem.query.filter_by(id=item_id, user_id=g.user.id).first_or_404()
    quantity_raw = request.form.get("quantity", "1")

    try:
        quantity = int(quantity_raw)
    except ValueError:
        flash("Quantity must be a number.", "error")
        return redirect(url_for("cart"))

    if quantity <= 0:
        db.session.delete(item)
        db.session.commit()
        flash("Item removed from cart.", "success")
        return redirect(url_for("cart"))

    if quantity > item.product.stock:
        flash(f"Only {item.product.stock} item(s) available in stock.", "error")
        return redirect(url_for("cart"))

    item.quantity = quantity
    db.session.commit()
    flash("Cart updated.", "success")
    return redirect(url_for("cart"))


@app.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_cart_item(item_id: int):
    item = CartItem.query.filter_by(id=item_id, user_id=g.user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash("Item removed from cart.", "success")
    return redirect(url_for("cart"))


@app.route("/place-order", methods=["POST"])
@login_required
def place_order():
    address = request.form.get("address", "").strip()
    if not address:
        flash("Delivery address is required.", "error")
        return redirect(url_for("cart"))

    cart_items = CartItem.query.filter_by(user_id=g.user.id).all()
    if not cart_items:
        flash("Your cart is empty.", "error")
        return redirect(url_for("cart"))

    for item in cart_items:
        if item.quantity > item.product.stock:
            flash(f"Not enough stock for {item.product.name}.", "error")
            return redirect(url_for("cart"))

    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    order = Order(user_id=g.user.id, address=address, total_amount=total_amount)
    db.session.add(order)
    db.session.flush()

    for item in cart_items:
        item.product.stock -= item.quantity
        db.session.add(
            OrderItem(
                order_id=order.id,
                product_id=item.product.id,
                product_name=item.product.name,
                unit_price=item.product.price,
                quantity=item.quantity,
            )
        )
        db.session.delete(item)

    db.session.commit()
    flash(f"Order placed successfully. Order ID: {order.id}", "success")
    return redirect(url_for("my_orders"))


@app.route("/orders")
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=g.user.id).order_by(Order.created_at.desc()).all()
    return render_template("orders.html", orders=orders)


@app.route("/admin/products", methods=["GET", "POST"])
@admin_required
def admin_products():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price_raw = request.form.get("price", "").strip()
        stock_raw = request.form.get("stock", "").strip()

        if not name or not price_raw or not stock_raw:
            flash("Name, price and stock are required.", "error")
            return redirect(url_for("admin_products"))

        try:
            price = float(price_raw)
            stock = int(stock_raw)
        except ValueError:
            flash("Price must be a number and stock must be an integer.", "error")
            return redirect(url_for("admin_products"))

        if price <= 0 or stock < 0:
            flash("Price must be greater than 0 and stock cannot be negative.", "error")
            return redirect(url_for("admin_products"))

        db.session.add(Product(name=name, price=price, stock=stock))
        db.session.commit()
        flash("Product added.", "success")
        return redirect(url_for("admin_products"))

    products = Product.query.order_by(Product.id.desc()).all()
    return render_template("admin.html", products=products)


@app.route("/admin/update-price/<int:product_id>", methods=["POST"])
@admin_required
def update_price(product_id: int):
    price_raw = request.form.get("price", "").strip()
    try:
        price = float(price_raw)
    except ValueError:
        flash("Invalid price.", "error")
        return redirect(url_for("admin_products"))

    if price <= 0:
        flash("Price must be greater than 0.", "error")
        return redirect(url_for("admin_products"))

    product = Product.query.get_or_404(product_id)
    product.price = price
    db.session.commit()
    flash("Price updated.", "success")
    return redirect(url_for("admin_products"))


@app.route("/admin/delete-product/<int:product_id>", methods=["POST"])
@admin_required
def delete_product(product_id: int):
    product = Product.query.get_or_404(product_id)
    CartItem.query.filter_by(product_id=product.id).delete()
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "success")
    return redirect(url_for("admin_products"))


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
