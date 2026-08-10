#!/bin/bash

# Build script for Render deployment
echo "Starting build process..."

# Navigate to backend directory
cd backend

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Build completed successfully!"