from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import logging
import sys
import traceback

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
for key in os.environ:
    if not any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key']):
        logger.info(f"{key}: {os.environ.get(key)}")

# Configure database
try:
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable is not set!")
        database_url = 'postgresql://postgres:postgres@localhost:5432/ecommerce'
        logger.info(f"Using default database URL: {database_url}")
    else:
        logger.info(f"Found DATABASE_URL: {database_url}")
    
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        logger.info(f"Modified DATABASE_URL: {database_url}")

    # Basic SQLAlchemy configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    logger.info("Initializing SQLAlchemy...")
    db = SQLAlchemy(app)
    logger.info("SQLAlchemy initialized successfully")
    
except Exception as e:
    logger.error(f"Error during database configuration: {str(e)}")
    logger.error(traceback.format_exc())
    raise

@app.route('/')
def home():
    try:
        # Test database connection with simple query
        logger.info("Testing database connection...")
        with db.engine.connect() as conn:
            result = conn.execute('SELECT 1').scalar()
            logger.info(f"Database connection test result: {result}")
        
        return jsonify({
            'message': 'Welcome to E-commerce API',
            'status': 'running',
            'database_status': 'connected',
            'database_test': result
        })
    except Exception as e:
        error_msg = f"Error in home route: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal Server Error',
            'message': error_msg,
            'traceback': traceback.format_exc()
        }), 500

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
