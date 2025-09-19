# REST API Endpoints Documentation

## Base URL
```
https://api.example.com/v1
```

## Authentication
All protected endpoints require authentication using JWT Bearer tokens:
```
Authorization: Bearer <access_token>
```

## Response Format
All API responses follow this structure:
```json
{
  "success": true,
  "data": {},
  "message": "Success message",
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_123456789"
  }
}
```

Error responses:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Detailed error message",
    "details": []
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_123456789"
  }
}
```

---

## Authentication Endpoints

### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe",
      "is_verified": false,
      "created_at": "2024-01-01T00:00:00Z"
    },
    "access_token": "jwt_access_token",
    "refresh_token": "jwt_refresh_token"
  }
}
```

### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "remember_me": false
}
```

### Refresh Token
```http
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "jwt_refresh_token"
}
```

### Logout
```http
POST /auth/logout
```

### Forgot Password
```http
POST /auth/forgot-password
```

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

### Reset Password
```http
POST /auth/reset-password
```

**Request Body:**
```json
{
  "token": "reset_token",
  "new_password": "NewSecurePassword123!"
}
```

### Verify Email
```http
POST /auth/verify-email
```

**Request Body:**
```json
{
  "token": "verification_token"
}
```

---

## User Management Endpoints

### Get Current User
```http
GET /users/me
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "avatar_url": "https://example.com/avatar.jpg",
    "bio": "User bio",
    "is_verified": true,
    "created_at": "2024-01-01T00:00:00Z",
    "roles": [
      {
        "name": "user",
        "permissions": ["read:items", "create:comments"]
      }
    ]
  }
}
```

### Update User Profile
```http
PUT /users/me
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "bio": "Updated bio",
  "avatar_url": "https://example.com/new-avatar.jpg"
}
```

### Change Password
```http
PUT /users/me/password
```

**Request Body:**
```json
{
  "current_password": "CurrentPassword123!",
  "new_password": "NewSecurePassword123!"
}
```

### Get User by ID
```http
GET /users/:id
```

### List Users (Admin)
```http
GET /users
```

**Query Parameters:**
- `page` (number, default: 1)
- `limit` (number, default: 20, max: 100)
- `search` (string)
- `role` (string)
- `is_active` (boolean)
- `sort` (string, default: "created_at")
- `order` (string, default: "desc")

**Response:**
```json
{
  "success": true,
  "data": {
    "users": [...],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

### Update User (Admin)
```http
PUT /users/:id
```

### Delete User (Admin)
```http
DELETE /users/:id
```

### Assign Role (Admin)
```http
POST /users/:id/roles
```

**Request Body:**
```json
{
  "role_name": "admin",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

---

## Item Management Endpoints

### Create Item
```http
POST /items
```

**Request Body:**
```json
{
  "title": "Sample Item",
  "description": "Item description",
  "content": "Full content",
  "excerpt": "Brief excerpt",
  "category_id": "uuid",
  "tags": ["tag1", "tag2"],
  "status": "draft",
  "visibility": "public",
  "featured_image_url": "https://example.com/image.jpg",
  "metadata": {
    "custom_field": "value"
  }
}
```

### Get Item by ID
```http
GET /items/:id
```

### Get Item by Slug
```http
GET /items/slug/:slug
```

### List Items
```http
GET /items
```

**Query Parameters:**
- `page` (number, default: 1)
- `limit` (number, default: 20, max: 100)
- `category_id` (uuid)
- `author_id` (uuid)
- `tag` (string)
- `status` (string: draft, published, archived)
- `visibility` (string: public, private, protected)
- `search` (string)
- `sort` (string: created_at, updated_at, published_at, title, view_count)
- `order` (string: asc, desc)

### Update Item
```http
PUT /items/:id
```

### Delete Item (Soft Delete)
```http
DELETE /items/:id
```

### Publish Item
```http
POST /items/:id/publish
```

### Unpublish Item
```http
POST /items/:id/unpublish
```

---

## Category Management Endpoints

### Create Category
```http
POST /categories
```

**Request Body:**
```json
{
  "name": "Technology",
  "description": "Technology related items",
  "slug": "technology",
  "parent_id": "uuid",
  "sort_order": 0,
  "metadata": {
    "icon": "fas fa-laptop"
  }
}
```

### Get Category by ID
```http
GET /categories/:id
```

### List Categories
```http
GET /categories
```

**Query Parameters:**
- `parent_id` (uuid)
- `is_active` (boolean)
- `sort` (string: name, sort_order, created_at)
- `order` (string: asc, desc)

### Update Category
```http
PUT /categories/:id
```

### Delete Category
```http
DELETE /categories/:id
```

### Get Category Tree
```http
GET /categories/tree
```

---

## Tag Management Endpoints

### Create Tag
```http
POST /tags
```

**Request Body:**
```json
{
  "name": "javascript",
  "color": "#f7df1e",
  "description": "JavaScript programming"
}
```

### Get Tag by ID
```http
GET /tags/:id
```

### List Tags
```http
GET /tags
```

**Query Parameters:**
- `search` (string)
- `sort` (string: name, usage_count, created_at)
- `order` (string: asc, desc)

### Update Tag
```http
PUT /tags/:id
```

### Delete Tag
```http
DELETE /tags/:id
```

---

## Comment Management Endpoints

### Create Comment
```http
POST /items/:itemId/comments
```

**Request Body:**
```json
{
  "content": "Great article!",
  "parent_id": "uuid" // Optional for replies
}
```

### Get Comments for Item
```http
GET /items/:itemId/comments
```

**Query Parameters:**
- `page` (number, default: 1)
- `limit` (number, default: 20, max: 100)
- `parent_id` (uuid) - for threaded comments
- `sort` (string: created_at, like_count)
- `order` (string: asc, desc)

### Get Comment by ID
```http
GET /comments/:id
```

### Update Comment
```http
PUT /comments/:id
```

**Request Body:**
```json
{
  "content": "Updated comment content"
}
```

### Delete Comment
```http
DELETE /comments/:id
```

### Approve Comment (Admin/Moderator)
```http
POST /comments/:id/approve
```

---

## Media Management Endpoints

### Upload File
```http
POST /media/upload
```

**Request Body (multipart/form-data):**
- `file` (file) - The file to upload
- `description` (string, optional)
- `alt_text` (string, optional)
- `is_public` (boolean, default: true)

### Get Media by ID
```http
GET /media/:id
```

### List Media
```http
GET /media
```

**Query Parameters:**
- `page` (number, default: 1)
- `limit` (number, default: 20, max: 100)
- `user_id` (uuid)
- `is_public` (boolean)
- `mime_type` (string)
- `sort` (string: created_at, file_size)
- `order` (string: asc, desc)

### Update Media
```http
PUT /media/:id
```

**Request Body:**
```json
{
  "description": "Updated description",
  "alt_text": "Updated alt text",
  "is_public": false
}
```

### Delete Media
```http
DELETE /media/:id
```

---

## API Key Management Endpoints

### Create API Key
```http
POST /api-keys
```

**Request Body:**
```json
{
  "name": "Mobile App",
  "permissions": ["read:items", "write:items"],
  "rate_limit": 1000,
  "expires_at": "2024-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Mobile App",
    "key": "api_key_here", // Only shown once
    "permissions": ["read:items", "write:items"],
    "rate_limit": 1000,
    "expires_at": "2024-12-31T23:59:59Z",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### List API Keys
```http
GET /api-keys
```

### Revoke API Key
```http
DELETE /api-keys/:id
```

---

## System Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0",
    "database": "connected",
    "redis": "connected"
  }
}
```

### System Info
```http
GET /system/info
```

**Response:**
```json
{
  "success": true,
  "data": {
    "version": "1.0.0",
    "environment": "production",
    "uptime": 86400,
    "memory_usage": {
      "used": 256,
      "total": 1024,
      "percentage": 25
    },
    "database": {
      "connections": 10,
      "max_connections": 100
    }
  }
}
```

### System Stats (Admin)
```http
GET /system/stats
```

**Response:**
```json
{
  "success": true,
  "data": {
    "users": {
      "total": 1000,
      "active": 850,
      "verified": 900
    },
    "items": {
      "total": 5000,
      "published": 4000,
      "draft": 1000
    },
    "comments": {
      "total": 10000,
      "pending_approval": 50
    },
    "api_calls": {
      "today": 50000,
      "this_month": 1500000
    }
  }
}
```

---

## Search Endpoints

### Search Items
```http
GET /search/items
```

**Query Parameters:**
- `q` (string) - Search query
- `category_id` (uuid)
- `tag` (string)
- `author_id` (uuid)
- `status` (string)
- `page` (number, default: 1)
- `limit` (number, default: 20, max: 100)

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "uuid",
        "title": "Search Result",
        "excerpt": "Item excerpt...",
        "author": {
          "id": "uuid",
          "username": "johndoe"
        },
        "category": {
          "id": "uuid",
          "name": "Technology"
        },
        "published_at": "2024-01-01T00:00:00Z",
        "relevance_score": 0.95
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "pages": 5
    },
    "search_metadata": {
      "query": "javascript",
      "execution_time": 0.05
    }
  }
}
```

### Search Users
```http
GET /search/users
```

### Search Comments
```http
GET /search/comments
```

---

## Webhook Endpoints

### Create Webhook
```http
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://example.com/webhook",
  "events": ["item.created", "item.updated", "user.registered"],
  "secret": "webhook_secret"
}
```

### List Webhooks
```http
GET /webhooks
```

### Update Webhook
```http
PUT /webhooks/:id
```

### Delete Webhook
```http
DELETE /webhooks/:id
```

---

## Rate Limits

All endpoints have rate limits:
- **Authenticated requests**: 1000 requests per hour
- **Unauthenticated requests**: 100 requests per hour
- **API Key requests**: Custom rate limit per key

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

---

## Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | VALIDATION_ERROR | Request validation failed |
| 401 | UNAUTHORIZED | Authentication required |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource conflict |
| 422 | UNPROCESSABLE_ENTITY | Semantic validation error |
| 429 | TOO_MANY_REQUESTS | Rate limit exceeded |
| 500 | INTERNAL_ERROR | Server error |
| 503 | SERVICE_UNAVAILABLE | Service temporarily unavailable |