from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Product, init_db

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    init_db(app)

@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    pid_str = str(product_id)  # Convert product_id to string
    cart[pid_str] = cart.get(pid_str, 0) + 1
    session['cart'] = cart
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    items = []
    total = 0
    for pid_str, qty in cart.items():
        pid = int(pid_str)  # Convert string back to int
        product = Product.query.get(pid)
        subtotal = qty * product.price
        items.append({'product': product, 'qty': qty, 'subtotal': subtotal})
        total += subtotal
    return render_template('cart.html', items=items, total=total)

@app.route('/checkout')
def checkout():
    session.pop('cart', None)
    return render_template('checkout.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
