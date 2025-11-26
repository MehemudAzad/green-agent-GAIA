#!/bin/bash

# Simple setup and run script for green and purple agents

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "=========================================="
echo "Green GAIA Agent - Setup & Run Guide"
echo "=========================================="
echo ""

# Check if dependencies are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip3 install flask google-genai python-dotenv pydantic requests -q
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

echo ""
echo "=========================================="
echo "Ready to run agents!"
echo "=========================================="
echo ""
echo "Option 1: Run Purple Agent (in background)"
echo "  Terminal 1: python3 -m purple_baseline.a2a_mock_server --port 8080"
echo ""
echo "Option 2: Run Green Evaluator (after purple is running)"
echo "  Terminal 2: python3 -m agent.evaluator --filename validation_complete.json --max-questions 5"
echo ""
echo "Option 3: Run via Docker"
echo "  cd docker && docker-compose up"
echo ""
