#!/bin/bash

# Deployment script for Express REST API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="express-rest-api"
REGISTRY_URL="${REGISTRY_URL:-localhost:5000}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo -e "${GREEN}🚀 Starting deployment of $PROJECT_NAME${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Build Docker image
echo -e "${YELLOW}📦 Building Docker image...${NC}"
docker build -t $PROJECT_NAME:$IMAGE_TAG .

# Tag image for registry
echo -e "${YELLOW}🏷️  Tagging image for registry...${NC}"
docker tag $PROJECT_NAME:$IMAGE_TAG $REGISTRY_URL/$PROJECT_NAME:$IMAGE_TAG

# Push to registry (if registry is specified)
if [ "$REGISTRY_URL" != "localhost:5000" ]; then
    echo -e "${YELLOW}📤 Pushing image to registry...${NC}"
    docker push $REGISTRY_URL/$PROJECT_NAME:$IMAGE_TAG
fi

# Stop and remove existing container
echo -e "${YELLOW}🛑 Stopping existing container...${NC}"
docker stop $PROJECT_NAME 2>/dev/null || true
docker rm $PROJECT_NAME 2>/dev/null || true

# Create network if it doesn't exist
echo -e "${YELLOW}🌐 Creating network...${NC}"
docker network create app-network 2>/dev/null || true

# Run new container
echo -e "${YELLOW}🚀 Starting new container...${NC}"
docker run -d \
    --name $PROJECT_NAME \
    --network app-network \
    --restart unless-stopped \
    -p 3000:3000 \
    -v $(pwd)/logs:/usr/src/app/logs \
    -e NODE_ENV=production \
    -e PORT=3000 \
    -e MONGODB_URI=mongodb://mongodb:27017/rest_api_db \
    -e JWT_SECRET=your_super_secret_jwt_key_here_change_in_production \
    -e JWT_EXPIRES_IN=7d \
    -e JWT_REFRESH_EXPIRES_IN=30d \
    -e BCRYPT_SALT_ROUNDS=12 \
    -e RATE_LIMIT_WINDOW_MS=900000 \
    -e RATE_LIMIT_MAX_REQUESTS=100 \
    -e LOG_LEVEL=info \
    -e CORS_ORIGIN=http://localhost:3000,http://localhost:3001 \
    $PROJECT_NAME:$IMAGE_TAG

# Wait for health check
echo -e "${YELLOW}⏳ Waiting for service to be healthy...${NC}"
timeout 60 bash -c 'until docker inspect --format="{{.State.Health.Status}}" express-rest-api 2>/dev/null | grep -q "healthy"; do sleep 2; done' || {
    echo -e "${RED}❌ Health check failed${NC}"
    docker logs $PROJECT_NAME
    exit 1
}

# Run database migration (if needed)
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
docker exec $PROJECT_NAME npm run migrate 2>/dev/null || true

# Run tests (optional)
if [ "$RUN_TESTS" = "true" ]; then
    echo -e "${YELLOW}🧪 Running tests...${NC}"
    docker exec $PROJECT_NAME npm test
fi

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}📊 Service status:${NC}"
docker ps --filter "name=$PROJECT_NAME"

echo -e "${YELLOW}📝 To view logs: docker logs -f $PROJECT_NAME${NC}"
echo -e "${YELLOW}🛑 To stop: docker stop $PROJECT_NAME${NC}"
echo -e "${YELLOW}🔄 To restart: docker restart $PROJECT_NAME${NC}"

# Health check endpoint
echo -e "${YELLOW}🔍 Health check: curl http://localhost:3000/health${NC}"