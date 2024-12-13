# E-commerce API

A RESTful API for managing e-commerce products, built with Flask and PostgreSQL.

## Features

- CRUD operations for products
- PostgreSQL database integration
- Automated CI/CD pipeline with GitHub Actions
- Deployment on Render
- Input validation and error handling
- Detailed logging

## API Endpoints

- `GET /`: Health check and database connection test
- `GET /api/products`: List all products
- `POST /api/products`: Create a new product
- `GET /api/products/<id>`: Get a specific product
- `PUT /api/products/<id>`: Update a product
- `DELETE /api/products/<id>`: Delete a product

## Product Schema

```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "price": "float (required, > 0)",
  "stock": "integer (optional, >= 0)"
}
```

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/e-commerce-api.git
cd e-commerce-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export DATABASE_URL=your_postgresql_url
export FLASK_ENV=production
```

4. Run the application:
```bash
python app.py
```

## Example API Usage

1. Create a product:
```bash
curl -X POST https://your-api-url/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "description": "A test product",
    "price": 29.99,
    "stock": 100
  }'
```

2. Get all products:
```bash
curl https://your-api-url/api/products
```

3. Get a specific product:
```bash
curl https://your-api-url/api/products/1
```

4. Update a product:
```bash
curl -X PUT https://your-api-url/api/products/1 \
  -H "Content-Type: application/json" \
  -d '{
    "price": 39.99,
    "stock": 50
  }'
```

5. Delete a product:
```bash
curl -X DELETE https://your-api-url/api/products/1
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- 200: Success
- 201: Created
- 400: Bad Request (validation error)
- 404: Not Found
- 500: Internal Server Error

## Deployment

The API is automatically deployed to Render when changes are pushed to the main branch. The deployment process includes:

1. Running tests
2. Building the application
3. Deploying to Render
4. Setting up the PostgreSQL database

## Environment Variables

Required environment variables:
- `DATABASE_URL`: PostgreSQL database URL
- `FLASK_ENV`: Application environment (production/development)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
