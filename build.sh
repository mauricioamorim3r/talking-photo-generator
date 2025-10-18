#!/usr/bin/env bash
# Build script for Render

set -o errexit  # Exit on error

echo "📦 Installing Python dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend build completed!"
