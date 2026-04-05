#!/bin/bash

echo "🔍 VehicleIQ Consistency Check"
echo "=============================="
echo ""

ERRORS=0

# Check 1: All relative paths in docker-compose
echo "✓ Checking docker-compose.yml..."
if grep -q "/Users/praveenkumar" docker-compose.yml 2>/dev/null; then
    echo "  ❌ Found absolute paths in docker-compose.yml"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ No absolute paths in docker-compose.yml"
fi

# Check 2: Backend Dockerfile uses relative paths
echo "✓ Checking backend/Dockerfile..."
if grep -q "/Users/praveenkumar" backend/Dockerfile 2>/dev/null; then
    echo "  ❌ Found absolute paths in backend/Dockerfile"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ No absolute paths in backend/Dockerfile"
fi

# Check 3: Frontend Dockerfile uses relative paths
echo "✓ Checking frontend/Dockerfile..."
if grep -q "/Users/praveenkumar" frontend/Dockerfile 2>/dev/null; then
    echo "  ❌ Found absolute paths in frontend/Dockerfile"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ No absolute paths in frontend/Dockerfile"
fi

# Check 4: Seed script uses relative paths
echo "✓ Checking scripts/seed.py..."
if grep -q "Path(__file__).parent.parent" scripts/seed.py; then
    echo "  ✅ Seed script uses relative path resolution"
else
    echo "  ❌ Seed script may have path issues"
    ERRORS=$((ERRORS + 1))
fi

# Check 5: Alembic uses environment variables
echo "✓ Checking backend/alembic/env.py..."
if grep -q "settings.DATABASE_URL" backend/alembic/env.py; then
    echo "  ✅ Alembic uses settings for database URL"
else
    echo "  ❌ Alembic may have hardcoded paths"
    ERRORS=$((ERRORS + 1))
fi

# Check 6: All required files exist
echo "✓ Checking required files..."
REQUIRED_FILES=(
    "docker-compose.yml"
    "backend/Dockerfile"
    "backend/requirements.txt"
    "backend/.env.example"
    "frontend/Dockerfile"
    "frontend/package.json"
    "frontend/.env.example"
    "scripts/init.sql"
    "scripts/seed.py"
    "services/paddleocr/Dockerfile"
    "services/yolo/Dockerfile"
    "services/embeddings/Dockerfile"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file exists"
    else
        echo "  ❌ $file missing"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check 7: Git repository is properly configured
echo "✓ Checking git configuration..."
if [ -d ".git" ]; then
    REMOTE=$(git remote get-url origin 2>/dev/null)
    if [ "$REMOTE" = "https://github.com/mpk112/vehicle-iq.git" ]; then
        echo "  ✅ Git remote correctly configured"
    else
        echo "  ❌ Git remote incorrect: $REMOTE"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  ❌ Not a git repository"
    ERRORS=$((ERRORS + 1))
fi

# Check 8: .gitignore excludes other_folder
echo "✓ Checking .gitignore..."
if grep -q "other_folder/" .gitignore; then
    echo "  ✅ other_folder/ is excluded"
else
    echo "  ❌ other_folder/ not in .gitignore"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "=============================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ All consistency checks passed!"
    echo ""
    echo "The codebase is:"
    echo "  ✅ Self-contained"
    echo "  ✅ Uses relative paths"
    echo "  ✅ Properly configured"
    echo "  ✅ Ready to run from any location"
    echo ""
    echo "You can safely:"
    echo "  - Clone this repo anywhere"
    echo "  - Run docker-compose up -d"
    echo "  - Share with team members"
    exit 0
else
    echo "❌ Found $ERRORS issue(s)"
    echo "Please review the errors above"
    exit 1
fi
