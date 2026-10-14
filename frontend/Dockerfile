# SmartMail AI — Production Frontend Dockerfile
# Stage 1: Build the React + Vite static bundle
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY package*.json ./
RUN npm ci

# Copy frontend source code
COPY . .

# Build-time API configuration (Defaults to empty string for relative or same-domain API routing)
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build production bundle
RUN npm run build

# Stage 2: Serve optimized static assets with Nginx
FROM nginx:1.27-alpine

# Remove default Nginx site configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration supporting SPA routing and security headers
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy compiled assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose HTTP port
EXPOSE 80

# Health check probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/healthz || exit 1

CMD ["nginx", "-g", "daemon off;"]
