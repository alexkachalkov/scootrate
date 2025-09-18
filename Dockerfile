# Stage 1: Build frontend
FROM node:18 AS frontend-builder

WORKDIR /app
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

# Stage 2: Backend and serve frontend
FROM python:3.12.3-slim

WORKDIR /app

# Install system dependencies including MySQL client libraries
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend

# Copy frontend build
COPY --from=frontend-builder /app/dist ./frontend/dist

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.app:app"]