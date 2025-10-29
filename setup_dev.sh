#!/bin/bash
# Development environment setup script

set -e

echo "=== Drupal News - Development Setup ==="
echo ""

# Check if in virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  No virtual environment detected."
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
    echo "Activate it with:"
    echo "  source venv/bin/activate"
    echo ""
    echo "Then run this script again."
    exit 0
fi

echo "✓ Virtual environment active: $VIRTUAL_ENV"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Compile SCSS
echo "Compiling SCSS to CSS..."
python3 src/compile_scss.py
echo "✓ SCSS compiled"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p runs cache static/css static/scss
echo "✓ Directories created"
echo ""

echo "=== Setup Complete! ==="
echo ""
echo "Available commands:"
echo "  make scss        - Compile SCSS"
echo "  make scss-watch  - Watch and auto-compile SCSS"
echo "  make viewer      - Start web viewer"
echo "  python3 index.py - Run aggregator"
echo ""
