#!/bin/bash

# VehicleIQ Phase 1 Testing Script
# This script automates the testing walkthrough

set -e  # Exit on error

echo "🚀 VehicleIQ Phase 1 Testing Script"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check prerequisites
echo "Step 1: Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi
print_success "Docker is installed"

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi
print_success "Docker Compose is installed"

# Check if Docker is running
if ! docker ps &> /dev/null; then
    print_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi
print_success "Docker is running"

echo ""
echo "Step 2: Setting up environment files..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    print_success "Created backend/.env"
else
    print_info "backend/.env already exists"
fi

if [ ! -f frontend/.env ]; then
    cp frontend/.env.example frontend/.env
    print_success "Created frontend/.env"
else
    print_info "frontend/.env already exists"
fi

echo ""
echo "Step 3: Starting Docker services..."
print_info "This may take 5-10 minutes on first run (downloading images and building)"
docker-compose up -d

echo ""
echo "Step 4: Waiting for services to be healthy..."
sleep 10

# Check service health
echo "Checking service status..."
docker-compose ps

echo ""
echo "Step 5: Running database migrations..."
sleep 5  # Give postgres a bit more time
docker-compose exec -T backend alembic upgrade head || {
    print_error "Migration failed. Checking logs..."
    docker-compose logs backend
    exit 1
}
print_success "Migrations completed"

echo ""
echo "Step 6: Seeding database with test data..."
docker-compose exec -T backend python scripts/seed.py || {
    print_error "Seeding failed. Checking logs..."
    docker-compose logs backend
    exit 1
}
print_success "Database seeded"

echo ""
echo "Step 7: Testing API endpoints..."

# Test health check
echo "Testing backend health check..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    print_success "Backend health check passed"
else
    print_error "Backend health check failed"
    echo "Response: $HEALTH_RESPONSE"
fi

# Test login
echo "Testing login endpoint..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@vehicleiq.com",
    "password": "Admin@123456"
  }')

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    print_success "Login endpoint works"
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    print_info "JWT Token obtained (first 50 chars): ${TOKEN:0:50}..."
else
    print_error "Login endpoint failed"
    echo "Response: $LOGIN_RESPONSE"
fi

echo ""
echo "Step 8: Testing AI microservices..."

# Test PaddleOCR
echo "Testing PaddleOCR service..."
PADDLE_RESPONSE=$(curl -s http://localhost:8001/health)
if echo "$PADDLE_RESPONSE" | grep -q "healthy"; then
    print_success "PaddleOCR service is healthy"
else
    print_error "PaddleOCR service is not responding"
fi

# Test YOLO
echo "Testing YOLO service..."
YOLO_RESPONSE=$(curl -s http://localhost:8002/health)
if echo "$YOLO_RESPONSE" | grep -q "healthy"; then
    print_success "YOLO service is healthy"
else
    print_error "YOLO service is not responding"
fi

# Test Embeddings
echo "Testing Embeddings service..."
EMB_RESPONSE=$(curl -s http://localhost:8003/health)
if echo "$EMB_RESPONSE" | grep -q "healthy"; then
    print_success "Embeddings service is healthy"
else
    print_error "Embeddings service is not responding"
fi

echo ""
echo "Step 9: Running backend tests..."
docker-compose exec -T backend pytest app/tests/unit/ -v || {
    print_error "Some tests failed"
}

echo ""
echo "=========================================="
echo "🎉 Testing Complete!"
echo "=========================================="
echo ""
echo "Access Points:"
echo "  Frontend:    http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs:    http://localhost:8000/docs"
echo ""
echo "Test Credentials:"
echo "  Admin:    admin@vehicleiq.com / Admin@123456"
echo "  Lender:   lender@example.com / Lender@123456"
echo "  Assessor: assessor@example.com / Assessor@123456"
echo ""
echo "Useful Commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart service:  docker-compose restart <service>"
echo ""
print_success "Phase 1 setup is complete and tested!"
