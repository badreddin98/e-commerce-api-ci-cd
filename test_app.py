import pytest
from app import app, db, Product, Order
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_home_page(client):
    """Test the home page endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'running'
    assert data['database_status'] == 'connected'

def test_create_product(client):
    """Test creating a new product"""
    product_data = {
        'name': 'Test Product',
        'description': 'A test product',
        'price': 29.99,
        'stock': 100
    }
    response = client.post('/api/products', 
                         json=product_data,
                         content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == product_data['name']
    assert float(data['price']) == product_data['price']
    assert data['stock'] == product_data['stock']

def test_get_products(client):
    """Test getting all products"""
    # Create a test product first
    product_data = {
        'name': 'Test Product',
        'price': 29.99,
        'stock': 100
    }
    client.post('/api/products', 
                json=product_data,
                content_type='application/json')
    
    # Get all products
    response = client.get('/api/products')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert data[0]['name'] == product_data['name']

def test_get_product(client):
    """Test getting a specific product"""
    # Create a test product first
    product_data = {
        'name': 'Test Product',
        'price': 29.99,
        'stock': 100
    }
    response = client.post('/api/products', 
                          json=product_data,
                          content_type='application/json')
    product_id = json.loads(response.data)['id']
    
    # Get the product
    response = client.get(f'/api/products/{product_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == product_data['name']

def test_update_product(client):
    """Test updating a product"""
    # Create a test product first
    product_data = {
        'name': 'Test Product',
        'price': 29.99,
        'stock': 100
    }
    response = client.post('/api/products', 
                          json=product_data,
                          content_type='application/json')
    product_id = json.loads(response.data)['id']
    
    # Update the product
    update_data = {
        'name': 'Updated Product',
        'price': 39.99
    }
    response = client.put(f'/api/products/{product_id}', 
                         json=update_data,
                         content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == update_data['name']
    assert float(data['price']) == update_data['price']

def test_delete_product(client):
    """Test deleting a product"""
    # Create a test product first
    product_data = {
        'name': 'Test Product',
        'price': 29.99,
        'stock': 100
    }
    response = client.post('/api/products', 
                          json=product_data,
                          content_type='application/json')
    product_id = json.loads(response.data)['id']
    
    # Delete the product
    response = client.delete(f'/api/products/{product_id}')
    assert response.status_code == 204
    
    # Verify product is deleted
    response = client.get(f'/api/products/{product_id}')
    assert response.status_code == 404

def test_validation_errors(client):
    """Test input validation"""
    # Test missing required field
    response = client.post('/api/products', 
                          json={'description': 'Missing name and price'},
                          content_type='application/json')
    assert response.status_code == 400
    
    # Test invalid price
    response = client.post('/api/products', 
                          json={'name': 'Test', 'price': -10},
                          content_type='application/json')
    assert response.status_code == 400
    
    # Test invalid stock
    response = client.post('/api/products', 
                          json={'name': 'Test', 'price': 10, 'stock': -1},
                          content_type='application/json')
    assert response.status_code == 400

def test_create_order(client):
    # Create a test product first
    product_response = client.post('/api/products', json={
        'name': 'Test Product',
        'price': 29.99,
        'stock': 100
    })
    product_id = json.loads(product_response.data)['id']
    
    # Create an order for the product
    response = client.post('/api/orders', json={
        'product_id': product_id,
        'quantity': 2
    })
    assert response.status_code == 201
    assert response.json['quantity'] == 2
    assert response.json['total_price'] == 59.98

def test_get_orders(client):
    # Create a test product first
    product_response = client.post('/api/products', json={
        'name': 'Test Product',
        'price': 29.99,
        'stock': 100
    })
    product_id = json.loads(product_response.data)['id']
    
    # Create an order for the product
    client.post('/api/orders', json={
        'product_id': product_id,
        'quantity': 2
    })
    
    # Get all orders
    response = client.get('/api/orders')
    assert response.status_code == 200
    assert len(response.json) > 0
    assert response.json[0]['quantity'] == 2

def test_get_order(client):
    # Create a test product first
    product_response = client.post('/api/products', json={
        'name': 'Test Product',
        'price': 29.99,
        'stock': 100
    })
    product_id = json.loads(product_response.data)['id']
    
    # Create an order for the product
    order_response = client.post('/api/orders', json={
        'product_id': product_id,
        'quantity': 2
    })
    order_id = json.loads(order_response.data)['id']
    
    # Get the order
    response = client.get(f'/api/orders/{order_id}')
    assert response.status_code == 200
    assert response.json['quantity'] == 2

def test_update_order(client):
    # Create a test product first
    product_response = client.post('/api/products', json={
        'name': 'Test Product',
        'price': 29.99,
        'stock': 100
    })
    product_id = json.loads(product_response.data)['id']
    
    # Create an order for the product
    order_response = client.post('/api/orders', json={
        'product_id': product_id,
        'quantity': 2
    })
    order_id = json.loads(order_response.data)['id']
    
    # Update the order
    update_data = {
        'quantity': 3
    }
    response = client.put(f'/api/orders/{order_id}', 
                         json=update_data,
                         content_type='application/json')
    assert response.status_code == 200
    assert response.json['quantity'] == 3

def test_delete_order(client):
    # Create a test product first
    product_response = client.post('/api/products', json={
        'name': 'Test Product',
        'price': 29.99,
        'stock': 100
    })
    product_id = json.loads(product_response.data)['id']
    
    # Create an order for the product
    order_response = client.post('/api/orders', json={
        'product_id': product_id,
        'quantity': 2
    })
    order_id = json.loads(order_response.data)['id']
    
    # Delete the order
    response = client.delete(f'/api/orders/{order_id}')
    assert response.status_code == 204
    
    # Verify order is deleted
    response = client.get(f'/api/orders/{order_id}')
    assert response.status_code == 404
