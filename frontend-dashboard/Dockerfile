# Multi-stage Dockerfile for Project Sentinel Frontend Dashboard
# Cameroon Defense Force OSINT Analysis System - React Frontend

# Stage 1: Build stage
FROM node:18-alpine as builder

# Set metadata labels
LABEL maintainer="Project Sentinel Frontend Team"
LABEL version="1.0"
LABEL description="React frontend dashboard for Project Sentinel OSINT system"
LABEL classification="RESTRICTED"

# Set working directory
WORKDIR /app

# Install dependencies first (better caching)
COPY package.json package-lock.json* ./
RUN npm ci --only=production --silent

# Copy source code
COPY . .

# Build arguments for environment configuration
ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_MAPBOX_ACCESS_TOKEN=""
ARG VITE_APP_VERSION=1.0.0

# Set environment variables for build
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_MAPBOX_ACCESS_TOKEN=$VITE_MAPBOX_ACCESS_TOKEN
ENV VITE_APP_VERSION=$VITE_APP_VERSION
ENV NODE_ENV=production

# Build the application
RUN npm run build

# Stage 2: Production stage
FROM nginx:alpine

# Security: Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Install security updates
RUN apk upgrade --no-cache

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create nginx cache directory
RUN mkdir -p /var/cache/nginx && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Install curl for health check
RUN apk add --no-cache curl

# Expose port
EXPOSE 80

# Switch to non-root user
USER nginx

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
