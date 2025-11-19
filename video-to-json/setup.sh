#!/bin/bash

# Setup script for extract-slides-from-video
# This script will set up the environment and install dependencies

set -e  # Exit on error

echo "=========================================="
echo "🎓 Slide Extractor Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || {
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
}

# Check if Tesseract is installed
echo "Checking Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract found: $(tesseract --version | head -n 1)"
else
    echo "❌ Tesseract OCR not found!"
    echo ""
    echo "Please install Tesseract:"
    echo "  macOS:   brew install tesseract"
    echo "  Ubuntu:  sudo apt-get install tesseract-ocr"
    echo "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
    echo ""
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create output directory
echo ""
echo "Creating output directory..."
mkdir -p output

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "To use the module:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Update VIDEO_PATH in example.py"
echo "  3. Run: python example.py"
echo ""
echo "To run tests:"
echo "  pytest tests/test_extractor.py -v"
echo ""
