#!/bin/bash

echo "🔍 VehicleIQ Phase 1 Verification"
echo "=================================="
echo ""

# Check directory structure
echo "✓ Checking directory structure..."
for dir in backend frontend services scripts .kiro; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir exists"
    else
        echo "  ✗ $dir missing"
        exit 1
    fi
done

# Check key files
echo ""
echo "✓ Checking key files..."
for file in docker-compose.yml README.md START_HERE.md Makefile; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file missing"
        exit 1
    fi
done

# Check backend files
echo ""
echo "✓ Checking backend files..."
for file in backend/requirements.txt backend/Dockerfile backend/.env.example backend/alembic.ini; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file missing"
        exit 1
    fi
done

# Check frontend files
echo ""
echo "✓ Checking frontend files..."
for file in frontend/package.json frontend/Dockerfile frontend/.env.example; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file missing"
        exit 1
    fi
done

# Check AI services
echo ""
echo "✓ Checking AI services..."
for service in paddleocr yolo embeddings; do
    if [ -f "services/$service/Dockerfile" ] && [ -f "services/$service/requirements.txt" ]; then
        echo "  ✓ $service service complete"
    else
        echo "  ✗ $service service incomplete"
        exit 1
    fi
done

# Check git status
echo ""
echo "✓ Checking git status..."
if [ -d ".git" ]; then
    echo "  ✓ Git repository initialized"
    REMOTE=$(git remote get-url origin 2>/dev/null)
    if [ -n "$REMOTE" ]; then
        echo "  ✓ Remote configured: $REMOTE"
    else
        echo "  ✗ No remote configured"
        exit 1
    fi
else
    echo "  ✗ Not a git repository"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ Phase 1 verification complete!"
echo ""
echo "Ready to test. Run:"
echo "  ./test-setup.sh"
echo ""
echo "Or follow:"
echo "  START_HERE.md"
