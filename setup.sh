#!/bin/bash
# Setup script for AI Eye Blink Checker

set -e

echo "================================================"
echo "AI Eye Blink Checker - Setup Script"
echo "================================================"
echo ""

# Check if uv is installed
if command -v uv &> /dev/null; then
    echo "✅ uv is already installed"
    echo "📦 Installing dependencies with uv..."
    uv sync
    echo ""
    echo "✅ Setup complete! You can now run:"
    echo "   uv run blink-checker"
else
    echo "⚠️  uv is not installed"
    echo ""
    echo "Option 1: Install uv (recommended)"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  Then run this script again"
    echo ""
    echo "Option 2: Use standard Python venv"
    read -p "Do you want to use standard Python venv? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv .venv
        
        echo "📦 Activating virtual environment..."
        source .venv/bin/activate
        
        echo "📦 Installing dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
        
        echo ""
        echo "✅ Setup complete! To use the application:"
        echo "   source .venv/bin/activate"
        echo "   python -m blink_checker.main"
        echo ""
        echo "Or run directly:"
        echo "   .venv/bin/python -m blink_checker.main"
    fi
fi

echo ""
echo "================================================"

