from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import logging
import sys
import traceback
import time

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
    # Try getting the full DATABASE_URL first
    database_url = os.environ.get('DATABASE_URL')
    
    # If not available, construct from individual components
    if not database_url:
        logger.info("DATABASE_URL not found, constructing from components...")
        db_user = os.environ.get('POSTGRES_USER')
        db_password = os.environ.get('POSTGRES_PASSWORD')
        db_host = os.environ.get('POSTGRES_HOST')
        db_port = os.environ.get('POSTGRES_PORT')
        db_name = os.environ.get('POSTGRES_DB')
        
        if all([db_user, db_password, db_host, db_port, db_name]):
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            logger.info("Successfully constructed DATABASE_URL from components")
        else:
            missing = []
            if not db_user: missing.append('POSTGRES_USER')
            if not db_password: missing.append('POSTGRES_PASSWORD')
            if not db_host: missing.append('POSTGRES_HOST')
            if not db_port: missing.append('POSTGRES_PORT')
            if not db_name: missing.append('POSTGRES_DB')
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
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
