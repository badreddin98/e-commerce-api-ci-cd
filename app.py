from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
import logging
import sys
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Log environment variables
logger.info("Environment variables:")
env_vars = {}
for key in os.environ:
    if not any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key']):
        env_vars[key] = os.environ.get(key)
logger.info(f"Environment variables: {env_vars}")

# Configure database
try:
    # Try getting the database URL from different environment variables
    database_url = os.environ.get('DATABASE_URL') or os.environ.get('PostgreSQL_database')
    
    if not database_url:
        raise ValueError("No database URL found in environment variables")
    
    # Convert postgres:// to postgresql:// if necessary
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    logger.info(f"Using database URL schema: {database_url.split('@')[0].split(':')[0]}")
    
    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'connect_args': {
                'connect_timeout': 10
            }
        }
    )
    
    logger.info("Initializing SQLAlchemy...")
    db = SQLAlchemy(app)
    logger.info("SQLAlchemy initialized successfully")
    
except Exception as e:
    logger.error(f"Error during database configuration: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Create tables
with app.app_context():
    db.create_all()
    logger.info("Database tables created successfully")

@app.route('/')
def home():
    try:
        logger.info("Testing database connection...")
        # Try to establish a connection
        with app.app_context():
            with db.engine.connect() as connection:
                result = connection.execute('SELECT 1').scalar()
                logger.info(f"Database connection test successful. Result: {result}")
        
        return jsonify({
            'message': 'Welcome to E-commerce API',
            'status': 'running',
            'database_status': 'connected',
            'database_test': result
        })
    except Exception as e:
        error_msg = f"Database connection error: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal Server Error',
            'message': error_msg,
            'traceback': traceback.format_exc()
        }), 500

# Product endpoints
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        products = Product.query.all()
        return jsonify([product.to_dict() for product in products])
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        product = Product(
            name=data['name'],
            description=data.get('description'),
            price=float(data['price']),
            stock=int(data.get('stock', 0))
        )
        db.session.add(product)
        db.session.commit()
        return jsonify(product.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating product: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    try:
        product = Product.query.get_or_404(id)
        return jsonify(product.to_dict())
    except Exception as e:
        logger.error(f"Error getting product {id}: {str(e)}")
        return jsonify({'error': str(e)}), 404

@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    try:
        product = Product.query.get_or_404(id)
        data = request.get_json()
        
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = float(data.get('price', product.price))
        product.stock = int(data.get('stock', product.stock))
        
        db.session.commit()
        return jsonify(product.to_dict())
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating product {id}: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    try:
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting product {id}: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.errorhandler(500)
def handle_500(error):
    error_msg = f"Internal Server Error: {str(error)}"
    logger.error(error_msg)
    logger.error(traceback.format_exc())
    return jsonify({
        'error': 'Internal Server Error',
        'message': error_msg,
        'traceback': traceback.format_exc()
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
