import pytest
from app import app, db, Product

@pytest.fixture
def client():
    # Setup test config
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory test DB
    app.config['SECRET_KEY'] = 'testkey'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # Add mock products
            product1 = Product(product_name="Test Product 1", price=99.99)
            product2 = Product(product_name="Test Product 2", price=149.49)
            db.session.add_all([product1, product2])
            db.session.commit()

        yield client

        # Clean up
        with app.app_context():
            db.drop_all()

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Test Product 1' in response.data
    assert b'Test Product 2' in response.data

def test_add_to_cart(client):
    response = client.get('/add_to_cart/1', follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as session:
        assert 'cart' in session
        assert '1' in session['cart']
        assert session['cart']['1']['qty'] == 1

def test_add_to_cart_multiple_times(client):
    client.get('/add_to_cart/1')
    client.get('/add_to_cart/1')
    with client.session_transaction() as session:
        assert session['cart']['1']['qty'] == 2

def test_cart_contents(client):
    client.get('/add_to_cart/1')
    response = client.get('/cart')
    assert response.status_code == 200
    assert b'Test Product 1' in response.data
    assert b'Total' in response.data

def test_checkout_clears_cart(client):
    client.get('/add_to_cart/1')
    response = client.get('/checkout')
    assert response.status_code == 200
    with client.session_transaction() as session:
        assert 'cart' not in session
