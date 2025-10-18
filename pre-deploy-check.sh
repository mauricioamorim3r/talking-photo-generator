#!/usr/bin/env bash
# Test script before deploying to Render

echo "🧪 Running pre-deploy checks..."
echo ""

# Check if all required files exist
echo "📋 Checking required files..."
required_files=(
    "render.yaml"
    "Procfile"
    "runtime.txt"
    "build.sh"
    "backend/requirements.txt"
    "backend/server.py"
    "frontend/package.json"
    "RENDER_DEPLOY.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING!"
        exit 1
    fi
done

echo ""
echo "🔍 Checking environment variables..."

# Check if .env exists (local development)
if [ -f "frontend/.env" ]; then
    echo "✅ frontend/.env exists"
    if grep -q "REACT_APP_BACKEND_URL" frontend/.env; then
        echo "✅ REACT_APP_BACKEND_URL is set"
    else
        echo "⚠️  REACT_APP_BACKEND_URL not found in frontend/.env"
    fi
else
    echo "⚠️  frontend/.env not found (will use defaults)"
fi

echo ""
echo "🐍 Checking Python dependencies..."
if command -v python &> /dev/null; then
    cd backend
    if pip install -r requirements.txt --dry-run &> /dev/null; then
        echo "✅ Python dependencies are valid"
    else
        echo "❌ Python dependencies have issues"
        cd ..
        exit 1
    fi
    cd ..
else
    echo "⚠️  Python not found, skipping dependency check"
fi

echo ""
echo "📦 Checking Node dependencies..."
if command -v npm &> /dev/null; then
    cd frontend
    if npm install --legacy-peer-deps --dry-run &> /dev/null; then
        echo "✅ Node dependencies are valid"
    else
        echo "❌ Node dependencies have issues"
        cd ..
        exit 1
    fi
    cd ..
else
    echo "⚠️  Node not found, skipping dependency check"
fi

echo ""
echo "🔐 Required API Keys for Render:"
echo "   - GEMINI_KEY"
echo "   - ELEVENLABS_API_KEY"
echo "   - FAL_KEY"
echo "   - CLOUDINARY_CLOUD_NAME"
echo "   - CLOUDINARY_API_KEY"
echo "   - CLOUDINARY_API_SECRET"

echo ""
echo "✅ All pre-deploy checks passed!"
echo ""
echo "📝 Next steps:"
echo "   1. Commit and push all changes to GitHub"
echo "   2. Go to https://dashboard.render.com"
echo "   3. Create a new Blueprint from your repository"
echo "   4. Add the environment variables listed above"
echo "   5. Deploy!"
echo ""
echo "📚 For detailed instructions, see: RENDER_DEPLOY.md"
