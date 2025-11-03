#!/bin/bash
# Complete setup script for Drupal News Aggregator
# This script sets up the entire project with virtual environment

set -e

echo "======================================"
echo "Drupal News Aggregator Setup"
echo "======================================"
echo

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python version: $PYTHON_VERSION"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -d "src" ]; then
    echo "❌ Error: Run this script from the project root directory"
    exit 1
fi

# Virtual environment setup
echo
echo "======================================"
echo "Step 1: Virtual Environment"
echo "======================================"

if [ -d "venv" ]; then
    echo "⚠ Virtual environment already exists at ./venv"
    read -p "Recreate it? This will delete the existing venv [y/N]: " recreate_venv
    if [[ $recreate_venv =~ ^[Yy]$ ]]; then
        echo "Removing old virtual environment..."
        rm -rf venv
    else
        echo "Using existing virtual environment"
    fi
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo
echo "======================================"
echo "Step 2: Dependencies"
echo "======================================"
echo "Upgrading pip..."
pip install --upgrade pip -q
echo "✓ pip upgraded"

# Install dependencies
echo "Installing project dependencies..."
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# Setup configuration
echo
echo "======================================"
echo "Step 3: Configuration"
echo "======================================"

if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "Creating .env file from template..."
        cp .env.example .env
        echo "✓ .env created - IMPORTANT: Edit with your credentials"
        echo "  📝 Edit: vim .env"
    else
        echo "⚠ Warning: .env.example not found, creating minimal .env"
        cat > .env << 'EOF'
# Timezone
TIMEZONE=Europe/Athens

# SMTP Settings (required for email)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASS=your-password
MAIL_TO=recipient@example.com
MAIL_FROM=sender@example.com
SMTP_TIMEOUT=10

# Retention settings
LOG_RETENTION_DAYS=45
RUN_RETENTION_DAYS=90

# Cache settings
CACHE_DB_PATH=./cache/cache.db
CACHE_TTL_DAYS=21
EOF
        echo "✓ Basic .env created - IMPORTANT: Edit with your credentials"
    fi
else
    echo "✓ .env already exists"
fi

# Verify config files
if [ ! -f config.json ]; then
    echo "⚠ Warning: config.json not found"
else
    echo "✓ config.json found"
fi

if [ ! -f providers.yaml ]; then
    echo "⚠ Warning: providers.yaml not found"
else
    echo "✓ providers.yaml found"
fi

# Create necessary directories
echo
echo "======================================"
echo "Step 4: Directories"
echo "======================================"
echo "Creating necessary directories..."
mkdir -p runs cache static/css static/scss
echo "✓ runs/ directory created"
echo "✓ cache/ directory created"
echo "✓ static/css/ directory created"
echo "✓ static/scss/ directory created"

# Compile SCSS
echo
echo "======================================"
echo "Step 5: SCSS Compilation"
echo "======================================"
if [ -f "src/compile_scss.py" ] && [ -f "static/scss/viewer.scss" ]; then
    echo "Compiling SCSS to CSS..."
    python3 src/compile_scss.py
    echo "✓ SCSS compiled to static/css/viewer.css"
else
    echo "⚠ Warning: SCSS compiler or source files not found, skipping"
fi

# Make scripts executable
echo
echo "======================================"
echo "Step 6: Scripts"
echo "======================================"
echo "Making scripts executable..."
chmod +x index.py scheduler.py send_email.py viewer.py 2>/dev/null || true
chmod +x src/compile_scss.py 2>/dev/null || true
echo "✓ Scripts are executable"

# Test basic functionality
echo
echo "======================================"
echo "Step 7: Verification"
echo "======================================"
echo "Testing basic imports..."

if python3 -c "import sys; sys.path.insert(0, 'src'); from drupal_news.utils import timebox; from drupal_news import cache_manager; from drupal_news import validator; from drupal_news.utils.dedupe import dedupe_items; from drupal_news.pdf_generator import generate_summary_pdf; print('✓ All imports successful')" 2>/dev/null; then
    echo "✓ Core modules loaded successfully"
else
    echo "⚠ Warning: Some modules failed to import (may need API keys)"
fi

# Test wrapper scripts
echo "Testing wrapper scripts..."
if python3 index.py --help > /dev/null 2>&1; then
    echo "✓ index.py works correctly"
else
    echo "⚠ Warning: index.py check failed"
fi

if python3 scheduler.py --help > /dev/null 2>&1; then
    echo "✓ scheduler.py works correctly"
else
    echo "⚠ Warning: scheduler.py check failed"
fi

if python3 send_email.py --help > /dev/null 2>&1; then
    echo "✓ send_email.py works correctly"
else
    echo "⚠ Warning: send_email.py check failed"
fi

# Summary
echo
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo
echo "📝 Next Steps:"
echo
echo "1. Edit .env with your API keys and SMTP settings:"
echo "   nano .env"
echo
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo
echo "3. Run a dry-run test (no AI, no email):"
echo "   ./index.py --dry-run --verbose"
echo
echo "4. Collect sources only (no AI):"
echo "   ./index.py --fetch-only --days 7"
echo
echo "5. Generate summary from cached sources:"
echo "   ./index.py --use-sources 2025-10-25 --provider anthropic"
echo
echo "6. Run full pipeline with AI provider:"
echo "   ./index.py --provider openai --days 7"
echo
echo "7. Send email from existing run:"
echo "   ./send_email.py --latest --days 7"
echo
echo "8. Setup scheduling (runs in background):"
echo "   ./scheduler.py --every friday --hour 9 --minute 0 --provider openai"
echo
echo "9. Web viewer commands:"
echo "   make scss        - Compile SCSS to CSS"
echo "   make scss-watch  - Watch and auto-compile SCSS"
echo "   make viewer      - Start web viewer (http://localhost:5000)"
echo
echo "10. To deactivate venv when done:"
echo "    deactivate"
echo
echo
echo "⚠ IMPORTANT: Always activate venv before running:"
echo "   source venv/bin/activate"
echo

# Keep venv activated for immediate use
echo "Virtual environment is still active. Run 'deactivate' to exit."
