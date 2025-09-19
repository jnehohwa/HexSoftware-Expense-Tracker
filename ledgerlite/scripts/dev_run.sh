#!/bin/bash

# Development run script for LedgerLite
# This script sets up the development environment and runs the application

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting LedgerLite Development Environment"
echo "Project root: $PROJECT_ROOT"

# Change to project root
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -e .

# Initialize database with sample data
echo "🗄️  Initializing database..."
python -c "
from ledgerlite.data.db import init_database
from ledgerlite.data.seed import seed_database
init_database()
seed_database()
print('Database initialized with sample data!')
"

# Run the application
echo "🎯 Starting LedgerLite..."
python -m ledgerlite.app.main

echo "👋 LedgerLite development session ended"

