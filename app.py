from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://localhost/ecommerce')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to E-commerce API',
        'status': 'running',
        'database': 'configured',
        'endpoints': {
            'products': '/products',
            'orders': '/orders'
        }
    })

@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'GET':
        products = Product.query.all()
        return jsonify([{'id': p.id, 'name': p.name, 'price': p.price} for p in products])
    elif request.method == 'POST':
        data = request.get_json()
        product = Product(name=data['name'], price=data['price'])
        db.session.add(product)
        db.session.commit()
        return jsonify({'id': product.id, 'name': product.name, 'price': product.price}), 201

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'GET':
        orders = Order.query.all()
        return jsonify([{'id': o.id, 'product_id': o.product_id, 'quantity': o.quantity, 'total_price': o.total_price} for o in orders])
    elif request.method == 'POST':
        data = request.get_json()
        product = Product.query.get(data['product_id'])
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        total_price = product.price * data['quantity']
        order = Order(product_id=data['product_id'], quantity=data['quantity'], total_price=total_price)
        db.session.add(order)
        db.session.commit()
        return jsonify({'id': order.id, 'product_id': order.product_id, 'quantity': order.quantity, 'total_price': order.total_price}), 201

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
