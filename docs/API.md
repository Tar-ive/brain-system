# Express REST API Documentation

## Overview

This is a comprehensive REST API built with Node.js and Express.js, implementing CRUD operations, JWT authentication, input validation, and security best practices.

## Base URL

```
http://localhost:3000/api
```

## Authentication

The API uses JWT (JSON Web Token) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Response Format

All API responses follow this format:

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Response data
  }
}
```

Error responses:
```json
{
  "success": false,
  "message": "Error description",
  "errors": [
    // Validation errors if applicable
  ]
}
```

## Endpoints

### Authentication

#### Register User
- **POST** `/auth/register`
- **Description**: Register a new user account
- **Body**:
  ```json
  {
    "username": "string (3-30 chars, alphanumeric)",
    "email": "string (valid email)",
    "password": "string (8+ chars, uppercase, lowercase, number, special char)",
    "firstName": "string (2-50 chars)",
    "lastName": "string (2-50 chars)"
  }
  ```
- **Response**: User object with access and refresh tokens

#### Login
- **POST** `/auth/login`
- **Description**: Login with existing credentials
- **Body**:
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **Response**: User object with access and refresh tokens

#### Refresh Token
- **POST** `/auth/refresh`
- **Description**: Refresh access token using refresh token
- **Body**:
  ```json
  {
    "refreshToken": "string"
  }
  ```
- **Response**: New access and refresh tokens

#### Logout
- **POST** `/auth/logout`
- **Authentication**: Required
- **Description**: Logout current user

#### Get Current User
- **GET** `/auth/me`
- **Authentication**: Required
- **Description**: Get current user profile
- **Response**: User object

### Users

#### Get All Users
- **GET** `/users`
- **Authentication**: Required (Admin only)
- **Description**: Get all users with pagination
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `limit`: Items per page (default: 10, max: 100)
  - `role`: Filter by role (user, admin, moderator)
  - `isActive`: Filter by active status (true/false)
- **Response**: Paginated user list

#### Get User by ID
- **GET** `/users/:id`
- **Authentication**: Required
- **Description**: Get user by ID (users can only view their own profile)
- **Response**: User object

#### Update User
- **PUT** `/users/:id`
- **Authentication**: Required
- **Description**: Update user profile (users can only update their own profile)
- **Body**:
  ```json
  {
    "username": "string (optional)",
    "email": "string (optional)",
    "firstName": "string (optional)",
    "lastName": "string (optional)",
    "profileImage": "string (optional)"
  }
  ```
- **Response**: Updated user object

#### Change Password
- **POST** `/users/change-password`
- **Authentication**: Required
- **Description**: Change user password
- **Body**:
  ```json
  {
    "currentPassword": "string",
    "newPassword": "string (8+ chars, uppercase, lowercase, number, special char)"
  }
  ```
- **Response**: Success message

#### Deactivate User
- **PATCH** `/users/:id/deactivate`
- **Authentication**: Required (Admin only)
- **Description**: Deactivate user account
- **Response**: Success message

#### Activate User
- **PATCH** `/users/:id/activate`
- **Authentication**: Required (Admin only)
- **Description**: Activate user account
- **Response**: Success message

#### Delete User
- **DELETE** `/users/:id`
- **Authentication**: Required (Admin only)
- **Description**: Delete user account (soft delete)
- **Response**: Success message

### Products

#### Create Product
- **POST** `/products`
- **Authentication**: Required
- **Description**: Create new product
- **Body**:
  ```json
  {
    "name": "string (2-200 chars, required)",
    "description": "string (max 1000 chars, optional)",
    "price": "number (positive, required)",
    "category": "string (max 50 chars, required)",
    "stock": "integer (min 0, default: 0)",
    "sku": "string (alphanumeric, max 50 chars, optional)",
    "images": ["string (URL) array"],
    "tags": ["string array"]
  }
  ```
- **Response**: Created product object

#### Get All Products
- **GET** `/products`
- **Description**: Get all products with filtering, pagination, and sorting
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `limit`: Items per page (default: 10, max: 100)
  - `search`: Search term (searches name, description, category, tags)
  - `category`: Filter by category
  - `minPrice`: Minimum price filter
  - `maxPrice`: Maximum price filter
  - `inStock`: Filter by stock availability (true/false)
  - `tags`: Filter by tags (comma-separated)
  - `sortBy`: Sort field (default: createdAt)
  - `sortOrder`: Sort order (asc/desc, default: desc)
- **Response**: Paginated product list with filters

#### Get Product by ID
- **GET** `/products/:id`
- **Description**: Get product by ID
- **Response**: Product object

#### Update Product
- **PUT** `/products/:id`
- **Authentication**: Required
- **Description**: Update product
- **Body**:
  ```json
  {
    "name": "string (optional)",
    "description": "string (optional)",
    "price": "number (positive, optional)",
    "category": "string (optional)",
    "stock": "integer (min 0, optional)",
    "sku": "string (alphanumeric, optional)",
    "images": ["string (URL) array"],
    "tags": ["string array"]
  }
  ```
- **Response**: Updated product object

#### Delete Product
- **DELETE** `/products/:id`
- **Authentication**: Required
- **Description**: Soft delete product
- **Response**: Success message

#### Update Stock
- **PATCH** `/products/:id/stock`
- **Authentication**: Required
- **Description**: Update product stock
- **Body**:
  ```json
  {
    "quantity": "integer (positive to add, negative to subtract)"
  }
  ```
- **Response**: Updated product object

#### Get Products by Category
- **GET** `/products/category/:category`
- **Description**: Get products by category with pagination
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `limit`: Items per page (default: 10, max: 100)
- **Response**: Paginated product list

#### Search Products
- **GET** `/products/search`
- **Description**: Search products
- **Query Parameters**:
  - `q`: Search query (required)
  - `page`: Page number (default: 1)
  - `limit`: Items per page (default: 10, max: 100)
- **Response**: Paginated search results

## HTTP Status Codes

- **200** OK - Request successful
- **201** Created - Resource created successfully
- **400** Bad Request - Invalid input data
- **401** Unauthorized - Authentication required
- **403** Forbidden - Insufficient permissions
- **404** Not Found - Resource not found
- **429** Too Many Requests - Rate limit exceeded
- **500** Internal Server Error - Server error

## Error Handling

The API includes comprehensive error handling with detailed error messages:

- **Validation Errors**: Returns field-specific validation errors
- **Authentication Errors**: Clear messages for invalid/missing tokens
- **Authorization Errors**: Permission denied messages
- **Database Errors**: User-friendly messages for database issues
- **Rate Limiting**: Clear retry information

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with configurable salt rounds
- **Input Validation**: Comprehensive validation using Joi
- **Rate Limiting**: Configurable request rate limiting
- **Security Headers**: Helmet.js for security headers
- **Data Sanitization**: Protection against NoSQL injection and XSS
- **CORS**: Configurable CORS settings
- **Request Logging**: Comprehensive request/response logging

## Rate Limiting

The API implements rate limiting:
- **Default**: 100 requests per 15 minutes per IP
- **Configurable**: Set via environment variables

## Examples

### Register a new user
```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "JohnDoe123!",
    "firstName": "John",
    "lastName": "Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "JohnDoe123!"
  }'
```

### Create a product
```bash
curl -X POST http://localhost:3000/api/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Smartphone",
    "description": "Latest smartphone with advanced features",
    "price": 999.99,
    "category": "Electronics",
    "stock": 50,
    "sku": "PHONE-001"
  }'
```

### Get all products with pagination
```bash
curl "http://localhost:3000/api/products?page=1&limit=10&category=Electronics&sortBy=price&sortOrder=asc"
```

### Search products
```bash
curl "http://localhost:3000/api/products/search?q=phone&page=1&limit=5"
```

## Development

### Setup
1. Install dependencies: `npm install`
2. Create `.env` file from `.env.example`
3. Start MongoDB
4. Run development server: `npm run dev`

### Testing
- Run tests: `npm test`
- Run tests with coverage: `npm run test:coverage`
- Run tests in watch mode: `npm run test:watch`

### Scripts
- `npm start` - Start production server
- `npm run dev` - Start development server with auto-reload
- `npm test` - Run all tests
- `npm run lint` - Run code linting
- `npm run typecheck` - Run TypeScript type checking

## Environment Variables

See `.env.example` for all available environment variables.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License