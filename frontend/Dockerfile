# CryptoMiner Pro V30 - Frontend Dashboard Dockerfile
FROM node:18-alpine

# Set working directory
WORKDIR /app/frontend

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy frontend source
COPY . .

# Build application
RUN yarn build

# Serve built application
FROM nginx:alpine

# Copy built application
COPY --from=0 /app/frontend/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose frontend port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]