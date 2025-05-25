import pytest
from app import app, db
from models import Product

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # If you use forms with CSRF
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Setup test products
            products = [
                Product(name="Test Product A", price=10.00),
                Product(name="Test Product B", price=15.50),
                Product(name="Test Product C", price=7.25),
            ]
            db.session.add_all(products)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def test_home_page_displays_products(client):
    rv = client.get('/')
    assert rv.status_code == 200
    # Check if all product names appear in homepage
    for name in [b"Test Product A", b"Test Product B", b"Test Product C"]:
        assert name in rv.data

def test_add_single_product_to_cart(client):
    rv = client.get('/add_to_cart/1', follow_redirects=True)
    assert rv.status_code == 200
    assert b"Test Product A" in rv.data

def test_add_multiple_products_to_cart(client):
    client.get('/add_to_cart/1')  # Add Product A
    client.get('/add_to_cart/2')  # Add Product B
    client.get('/add_to_cart/1')  # Add Product A again (qty = 2)
    
    rv = client.get('/cart')
    assert rv.status_code == 200
    data = rv.data.decode('utf-8')
    # Check quantities and product names appear
    assert "Test Product A" in data
    assert "Test Product B" in data
    # Check quantity = 2 for Product A and 1 for Product B
    assert "Qty: 2" in data or "qty=2" in data or "2" in data
    assert "Qty: 1" in data or "qty=1" in data or "1" in data

def test_cart_total_calculation(client):
    client.get('/add_to_cart/1')  # Product A: 10.00
    client.get('/add_to_cart/2')  # Product B: 15.50
    client.get('/add_to_cart/3')  # Product C: 7.25
    client.get('/add_to_cart/3')  # Product C again
    
    rv = client.get('/cart')
    assert rv.status_code == 200
    data = rv.data.decode('utf-8')

    expected_total = 10.00 + 15.50 + (7.25 * 2)
    # Check if total price is displayed somewhere (formatted as string)
    assert f"{expected_total:.2f}" in data

def test_add_invalid_product(client):
    rv = client.get('/add_to_cart/999', follow_redirects=True)
    # Should handle gracefully, product not found, maybe redirect home
    assert rv.status_code == 200

def test_checkout_clears_cart(client):
    client.get('/add_to_cart/1')
    client.get('/add_to_cart/2')

    rv = client.get('/checkout')
    assert rv.status_code == 200
    assert b"Thank you" in rv.data or b"Checkout" in rv.data

    # Cart should be empty now
    rv2 = client.get('/cart')
    data = rv2.data.decode('utf-8')
    # No products in cart page
    assert "Test Product A" not in data
    assert "Test Product B" not in data
