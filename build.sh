#!/usr/bin/env bash
# Build script for Render

set -o errexit  # Exit on error

echo "📦 Installing Python dependencies..."
echo "Current directory: $(pwd)"
echo "Listing files: $(ls -la)"

cd backend
echo "Changed to backend directory: $(pwd)"
echo "Checking requirements.txt: $(ls -la requirements.txt)"

pip install --upgrade pip

# Try minimal requirements first (more flexible versions)
if [ -f requirements-minimal.txt ]; then
    echo "📦 Using requirements-minimal.txt for better compatibility..."
    pip install -r requirements-minimal.txt
else
    echo "📦 Using standard requirements.txt..."
    pip install -r requirements.txt
fi

echo "✅ Backend build completed!"
