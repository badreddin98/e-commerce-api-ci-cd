# E-commerce API with CI/CD

This is an E-commerce API built with Flask and PostgreSQL, featuring a complete CI/CD pipeline using GitHub Actions and deployment to Render.

## Features

- RESTful API endpoints for products and orders
- PostgreSQL database integration
- Swagger documentation
- Automated testing with pytest
- CI/CD pipeline with GitHub Actions
- Deployment to Render

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`:
   ```
   DATABASE_URL=your_postgres_url
   FLASK_APP=app.py
   FLASK_ENV=development
   ```
4. Run the application:
   ```bash
   flask run
   ```

## API Documentation

Access the Swagger documentation at `/api/docs` when running the application locally.

## Testing

Run tests using pytest:
```bash
pytest
```

## CI/CD Pipeline

The project uses GitHub Actions for CI/CD:
- Automated testing on push to main branch
- Automatic deployment to Render on successful tests
- PostgreSQL database hosted on Render

## Database Schema

- Products Table: id, name, price, description, created_at
- Orders Table: id, product_id, quantity, total_price, created_at
