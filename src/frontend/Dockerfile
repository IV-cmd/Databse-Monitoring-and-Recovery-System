# Simple multi-stage Dockerfile for Angular Frontend
# Following first principles: minimal, clean, purposeful

# Stage 1: Build the application
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci --silent

# Copy source and build
COPY . .
RUN npm run build

# Stage 2: Production with distroless
FROM gcr.io/distroless/static AS production

# Copy built application
COPY --from=builder /app/dist/frontend /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["/bin/sh", "-c", "wget --no-verbose --tries=1 --spider http://localhost/ || exit 1"]
