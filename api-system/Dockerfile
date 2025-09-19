# Use official Node.js runtime as a parent image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Create app user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    tzdata \
    && cp /usr/share/zoneinfo/America/New_York /etc/localtime \
    && echo "America/New_York" > /etc/timezone \
    && apk del tzdata

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy the rest of the application code
COPY . .

# Create directories and set permissions
RUN mkdir -p logs uploads && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Build the application (if needed)
RUN npm run build

# Expose the port the app runs on
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node healthcheck.js

# Environment variables
ENV NODE_ENV=production \
    PORT=3000 \
    DB_HOST=localhost \
    DB_PORT=5432 \
    REDIS_HOST=localhost \
    REDIS_PORT=6379

# Start the application
CMD ["npm", "start"]