import pytest
from app import app, db, Product, Order

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/test_db'
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_create_product(client):
    response = client.post('/products', json={
        'name': 'Test Product',
        'price': 99.99,
        'description': 'Test Description'
    })
    assert response.status_code == 201
    assert response.json['name'] == 'Test Product'
    assert response.json['price'] == 99.99

def test_get_products(client):
    # Create a test product
    client.post('/products', json={
        'name': 'Test Product',
        'price': 99.99,
        'description': 'Test Description'
    })
    
    response = client.get('/products')
    assert response.status_code == 200
    assert len(response.json) > 0
    assert response.json[0]['name'] == 'Test Product'

def test_create_order(client):
    # Create a test product first
    product_response = client.post('/products', json={
        'name': 'Test Product',
        'price': 99.99,
        'description': 'Test Description'
    })
    product_id = product_response.json['id']
    
    # Create an order for the product
    response = client.post('/orders', json={
        'product_id': product_id,
        'quantity': 2
    })
    assert response.status_code == 201
    assert response.json['quantity'] == 2
    assert response.json['total_price'] == 199.98
