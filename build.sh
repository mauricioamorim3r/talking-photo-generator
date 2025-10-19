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
pip install -r requirements.txt

echo "✅ Backend build completed!"
