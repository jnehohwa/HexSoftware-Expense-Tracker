#!/bin/bash

# LedgerLite Startup Script
# This script provides an easy way to start LedgerLite

echo "🚀 Starting LedgerLite..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Using system Python..."
fi

# Check if package is installed
if python -c "import ledgerlite" 2>/dev/null; then
    echo "✅ LedgerLite package found"
else
    echo "❌ LedgerLite package not found. Installing..."
    pip install -e .
fi

# Start the application
echo "📱 Launching LedgerLite..."
python -m ledgerlite.app.main

echo "👋 LedgerLite closed."


