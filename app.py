from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

# Log configuration details
logger.info(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
logger.info(f"PORT: {os.getenv('PORT', 'Not set')}")

# Configure database
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

logger.info(f"Final DATABASE_URL: {app.config['SQLALCHEMY_DATABASE_URI']}")

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
    try:
        logger.info("Creating database tables...")
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise

@app.route('/')
def home():
    try:
        return jsonify({
            'message': 'Welcome to E-commerce API',
            'status': 'running',
            'database': 'configured',
            'endpoints': {
                'products': '/products',
                'orders': '/orders'
            }
        })
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/products', methods=['GET', 'POST'])
def products():
    try:
        if request.method == 'GET':
            products = Product.query.all()
            return jsonify([{'id': p.id, 'name': p.name, 'price': p.price} for p in products])
        elif request.method == 'POST':
            data = request.get_json()
            logger.info(f"Received product data: {data}")
            product = Product(name=data['name'], price=data['price'])
            db.session.add(product)
            db.session.commit()
            return jsonify({'id': product.id, 'name': product.name, 'price': product.price}), 201
    except Exception as e:
        logger.error(f"Error in products route: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    try:
        if request.method == 'GET':
            orders = Order.query.all()
            return jsonify([{'id': o.id, 'product_id': o.product_id, 'quantity': o.quantity, 'total_price': o.total_price} for o in orders])
        elif request.method == 'POST':
            data = request.get_json()
            logger.info(f"Received order data: {data}")
            product = Product.query.get(data['product_id'])
            if not product:
                return jsonify({'error': 'Product not found'}), 404
            total_price = product.price * data['quantity']
            order = Order(product_id=data['product_id'], quantity=data['quantity'], total_price=total_price)
            db.session.add(order)
            db.session.commit()
            return jsonify({'id': order.id, 'product_id': order.product_id, 'quantity': order.quantity, 'total_price': order.total_price}), 201
    except Exception as e:
        logger.error(f"Error in orders route: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.errorhandler(500)
def handle_500(error):
    logger.error(f"Internal Server Error: {str(error)}")
    return jsonify({'error': 'Internal Server Error', 'message': str(error)}), 500

@app.errorhandler(404)
def handle_404(error):
    logger.error(f"Not Found Error: {str(error)}")
    return jsonify({'error': 'Not Found', 'message': str(error)}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
