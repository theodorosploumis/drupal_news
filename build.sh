#!/bin/bash
# Build script wrapper that ensures virtual environment is active

set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Ensure build tools are installed in venv
echo "Installing build tools in venv..."
pip install --upgrade build twine -q

# Run the build script with venv Python
echo "Running build script..."
python3 build_package.py "$@"

# Keep results
echo ""
echo "Build artifacts in dist/"
ls -lh dist/ 2>/dev/null || echo "No artifacts created yet"
