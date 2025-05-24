import pytest
from app import app, db, Product

@pytest.fixture
def client():
    # Use in-memory SQLite database for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def create_test_product():
    product = Product(product_name="Test Product", price=99.99)
    db.session.add(product)
    db.session.commit()
    return product

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Products" in response.data or b"Cart" in response.data

def test_add_to_cart(client):
    with app.app_context():
        product = create_test_product()

    response = client.get(f'/add_to_cart/{product.product_id}')
    assert response.status_code == 302  # Redirect to home

def test_add_to_cart_multiple_times(client):
    with app.app_context():
        product = create_test_product()

    for _ in range(3):
        client.get(f'/add_to_cart/{product.product_id}')

    with client.session_transaction() as session:
        cart = session.get('cart', {})
        assert str(product.product_id) in cart
        assert cart[str(product.product_id)]['qty'] == 3

def test_cart_contents(client):
    with app.app_context():
        product = create_test_product()

    client.get(f'/add_to_cart/{product.product_id}')
    response = client.get('/cart')
    assert response.status_code == 200
    assert b"Test Product" in response.data

def test_checkout_clears_cart(client):
    with app.app_context():
        product = create_test_product()

    client.get(f'/add_to_cart/{product.product_id}')
    response = client.get('/checkout')
    assert response.status_code == 200
    assert b"Thank you" in response.data or b"checkout" in response.data.lower()

    with client.session_transaction() as session:
        assert 'cart' not in session
