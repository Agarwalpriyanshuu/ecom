from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Replace with a strong secret key

# Database configuration — replace with your actual full AWS RDS URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:25258202Pr@database-1.cm14ws46qfvu.us-east-1.rds.amazonaws.com/product'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Product model definition
class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    @property
    def id(self):
        return self.product_id

    @property
    def name(self):
        return self.product_name

# Home route - show all products
@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)

# Add product to cart
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart = session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['qty'] += 1
    else:
        cart[str(product_id)] = {
            'product_id': product.id,
            'name': product.name,
            'price': product.price,
            'qty': 1
        }

    session['cart'] = cart
    return redirect(url_for('home'))

# View cart
@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    items = []
    total = 0.0

    for product_id, item in cart.items():
        qty = item['qty']
        product = Product.query.get(product_id)
        if product:
            items.append({'product': product, 'qty': qty})
            total += product.price * qty

    return render_template('cart.html', items=items, total=total)

# Checkout route
@app.route('/checkout')
def checkout():
    session.pop('cart', None)  # Clear cart on checkout
    return render_template('checkout.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
