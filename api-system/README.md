# Complete REST API System

A production-ready REST API system built with Node.js, TypeScript, and Express. This system includes comprehensive authentication, caching, monitoring, and deployment configurations.

## 🚀 Features

### Core Functionality
- **RESTful API Design**: Follows REST principles with proper HTTP methods and status codes
- **TypeScript**: Type-safe development with comprehensive type definitions
- **Modular Architecture**: Clean separation of concerns with layers architecture
- **Comprehensive Error Handling**: Structured error responses with proper HTTP status codes

### Authentication & Security
- **JWT Authentication**: Stateless authentication with access and refresh tokens
- **Role-Based Access Control (RBAC)**: Flexible permission system
- **API Key Management**: External access with customizable permissions
- **Security Middleware**: Rate limiting, CORS, XSS protection, SQL injection prevention
- **Password Security**: bcrypt hashing with configurable rounds
- **Session Management**: Secure session handling with Redis

### Database & Caching
- **PostgreSQL**: Robust relational database with comprehensive schema
- **Redis**: Multi-layer caching strategy with TTL management
- **Connection Pooling**: Optimized database connections
- **Query Optimization**: Indexed queries with performance monitoring
- **Cache Patterns**: Cache-aside, write-through, and read-through patterns

### Monitoring & Logging
- **Structured Logging**: Winston-based logging with JSON format
- **Metrics Collection**: Prometheus integration with custom metrics
- **Health Checks**: Comprehensive health check endpoints
- **Performance Monitoring**: Response time tracking and slow query detection
- **Error Tracking**: Centralized error logging with context

### Performance & Scalability
- **Rate Limiting**: Configurable rate limiting with different strategies
- **Compression**: Gzip compression for API responses
- **Load Balancing**: Horizontal scaling with containerization
- **Database Optimization**: Read replicas and query optimization
- **Caching Strategy**: Multi-level caching with automatic invalidation

### Deployment & DevOps
- **Docker Containerization**: Multi-stage Docker builds
- **Docker Compose**: Local development environment
- **Production Deployment**: Docker Swarm and Kubernetes ready
- **Environment Management**: Comprehensive environment configuration
- **CI/CD Pipeline**: Automated testing and deployment

## 📁 Project Structure

```
api-system/
├── src/
│   ├── controllers/          # Request handlers
│   ├── models/              # Data models and database operations
│   ├── services/            # Business logic layer
│   ├── middleware/          # Authentication, validation, error handling
│   ├── routes/              # Route definitions
│   ├── utils/               # Utility functions
│   ├── config/              # Configuration files
│   └── index.ts             # Application entry point
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── e2e/                 # End-to-end tests
├── docs/
│   ├── api/                 # API documentation
│   └── architecture/        # Architecture documentation
├── docker/
│   ├── nginx.conf           # Nginx configuration
│   └── init.sql             # Database initialization
├── deployments/
│   └── docker/              # Production deployment configs
├── scripts/                 # Utility scripts
└── docker-compose.yml       # Development environment
```

## 🛠️ Technology Stack

### Backend
- **Node.js** 18+ - Runtime environment
- **TypeScript** - Type safety and better development experience
- **Express.js** - Web framework
- **Winston** - Structured logging
- **Joi/Zod** - Data validation

### Database
- **PostgreSQL** 15+ - Primary database
- **Redis** 7+ - Caching and session storage
- **TypeORM** - ORM with active record and data mapper patterns

### Authentication
- **JWT** - JSON Web Tokens
- **bcrypt** - Password hashing
- **Passport.js** - Authentication middleware

### Security
- **Helmet** - Security headers
- **CORS** - Cross-origin resource sharing
- **express-rate-limit** - Rate limiting
- **express-validator** - Input validation
- **xss-clean** - XSS protection

### Monitoring
- **Prometheus** - Metrics collection
- **Grafana** - Visualization
- **Winston** - Logging
- **Elastic Stack** - Log aggregation (optional)

### Testing
- **Jest** - Testing framework
- **Supertest** - HTTP assertions
- **Artillery** - Load testing

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy
- **PM2** - Process management

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/api-system.git
   cd api-system
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start development environment with Docker**
   ```bash
   npm run docker:dev
   ```

5. **Run database migrations**
   ```bash
   npm run migrate
   ```

6. **Seed database with sample data**
   ```bash
   npm run seed
   ```

7. **Start the application**
   ```bash
   npm run dev
   ```

The API will be available at `http://localhost:3000`

### Using Docker Compose

1. **Start all services**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f
   ```

3. **Stop services**
   ```bash
   docker-compose down
   ```

### Manual Setup (without Docker)

1. **Install PostgreSQL and Redis**
2. **Create database**
   ```sql
   CREATE DATABASE api_system;
   ```

3. **Configure environment variables**
   ```env
   NODE_ENV=development
   PORT=3000
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=api_system
   DB_USER=postgres
   DB_PASSWORD=password
   REDIS_HOST=localhost
   REDIS_PORT=6379
   JWT_SECRET=your-super-secret-jwt-key
   JWT_REFRESH_SECRET=your-super-secret-refresh-jwt-key
   ```

4. **Run the application**
   ```bash
   npm install
   npm run build
   npm run migrate
   npm run seed
   npm start
   ```

## 📖 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | User login |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | User logout |
| POST | `/auth/forgot-password` | Request password reset |
| POST | `/auth/reset-password` | Reset password |
| POST | `/auth/verify-email` | Verify email address |

### User Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me` | Get current user profile |
| PUT | `/users/me` | Update user profile |
| PUT | `/users/me/password` | Change password |
| GET | `/users/:id` | Get user by ID |
| GET | `/users` | List users (Admin) |

### Item Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/items` | Create new item |
| GET | `/items/:id` | Get item by ID |
| PUT | `/items/:id` | Update item |
| DELETE | `/items/:id` | Delete item |
| GET | `/items` | List items with pagination |

### Monitoring Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |
| GET | `/system/info` | System information |

For complete API documentation, visit `/docs` when running the application.

## 🔧 Configuration

### Environment Variables

The application uses environment variables for configuration. Key variables include:

#### Application
- `NODE_ENV` - Environment (development, staging, production)
- `PORT` - Application port (default: 3000)
- `HOST` - Application host (default: 0.0.0.0)

#### Database
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password

#### Redis
- `REDIS_HOST` - Redis host
- `REDIS_PORT` - Redis port
- `REDIS_PASSWORD` - Redis password (optional)

#### JWT
- `JWT_SECRET` - JWT secret key (minimum 32 characters)
- `JWT_REFRESH_SECRET` - JWT refresh secret key (minimum 32 characters)

#### Security
- `BCRYPT_ROUNDS` - Password hashing rounds (default: 12)
- `RATE_LIMIT_MAX_REQUESTS` - Max requests per window (default: 100)
- `ALLOWED_ORIGINS` - CORS allowed origins (comma-separated)

### Environment-specific Configuration

The application supports different configurations for development, staging, and production environments. Each environment has its own Docker Compose configuration:

- `docker-compose.yml` - Development
- `deployments/docker/docker-compose.staging.yml` - Staging
- `deployments/docker/docker-compose.prod.yml` - Production

## 🧪 Testing

### Unit Tests
```bash
npm test
```

### Integration Tests
```bash
npm run test:integration
```

### End-to-End Tests
```bash
npm run test:e2e
```

### Test Coverage
```bash
npm run test:coverage
```

### Load Testing
```bash
npm run performance:test
```

## 🚀 Deployment

### Production Deployment with Docker

1. **Build the application**
   ```bash
   npm run build
   docker build -t api-system:latest .
   ```

2. **Deploy to production**
   ```bash
   docker-compose -f docker-compose.yml -f deployments/docker/docker-compose.prod.yml up -d
   ```

### Environment Variables for Production

Create a `.env.production` file with production-specific values:

```env
NODE_ENV=production
PORT=3000
DB_HOST=postgres
DB_PORT=5432
DB_NAME=api_system_prod
DB_USER=api_user
DB_PASSWORD=secure_database_password
REDIS_HOST=redis
REDIS_PORT=6379
JWT_SECRET=your-production-jwt-secret-key
JWT_REFRESH_SECRET=your-production-refresh-secret-key
LOG_LEVEL=info
MONITORING_ENABLED=true
```

### Scaling the Application

To scale the application, modify the `replicas` setting in the Docker Compose production configuration:

```yaml
services:
  api:
    deploy:
      replicas: 5  # Scale to 5 instances
```

## 📊 Monitoring

### Health Checks

The application provides multiple health check endpoints:

- `/health` - Basic health check
- `/health/ready` - Readiness check
- `/health/live` - Liveness check

### Metrics

Prometheus metrics are available at `/metrics`. Key metrics include:

- HTTP request count and duration
- Database query performance
- Cache hit rates
- Error rates
- System resource usage

### Logging

Logs are written to both console and files:

- `logs/combined.log` - All logs
- `logs/error.log` - Error logs only

### Visualization

Grafana dashboards are pre-configured for monitoring:

- Application performance
- Database metrics
- System resources
- Business metrics

## 🔒 Security

### Authentication

The system uses JWT-based authentication with the following features:

- Access tokens with short expiration (1 hour default)
- Refresh tokens with longer expiration (7 days default)
- Secure token storage
- Session invalidation on logout
- Password hashing with bcrypt

### Authorization

Role-based access control (RBAC) with:

- User roles and permissions
- API key-based authentication
- Resource ownership checks
- Flexible permission system

### Security Features

- Rate limiting with different strategies
- CORS configuration
- Security headers (Helmet)
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection
- Secure cookie settings

## 🏗️ Architecture

### Layered Architecture

The application follows a layered architecture pattern:

1. **Routes Layer** - HTTP endpoint definitions
2. **Controllers Layer** - Request handling and response formatting
3. **Services Layer** - Business logic implementation
4. **Models Layer** - Data access and database operations
5. **Database Layer** - Data persistence

### Design Patterns

- **Repository Pattern** - Abstract data access
- **Service Layer Pattern** - Business logic separation
- **Dependency Injection** - Loose coupling
- **Middleware Pattern** - Cross-cutting concerns
- **Factory Pattern** - Object creation
- **Observer Pattern** - Event handling

### Data Flow

```
HTTP Request → Routes → Controllers → Services → Models → Database
                                                    ↓
Response ← Controllers ← Services ← Models ← Cache ← Database
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`npm test`)
6. Run linting (`npm run lint`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Express.js team for the excellent web framework
- TypeScript team for bringing type safety to JavaScript
- Docker team for containerization technology
- PostgreSQL and Redis communities for robust data solutions
- All open-source contributors who made this project possible

## 📞 Support

If you have any questions or need support:

- Create an issue on GitHub
- Check the documentation in the `docs/` directory
- Review the API documentation at `/docs` when running

---

**Built with ❤️ using modern web technologies**