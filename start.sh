#!/bin/bash
# Bit Buddy Start Script
# This script automatically activates the virtual environment and runs the application

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at $VENV_DIR"
    echo ""
    echo "Please run setup first:"
    echo "  python3 setup.py"
    echo ""
    echo "This will:"
    echo "  1. Create a virtual environment"
    echo "  2. Install all dependencies"
    echo "  3. Guide you through initial configuration"
    exit 1
fi

# Check if activate script exists
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "❌ Virtual environment appears corrupted (activate script missing)"
    echo ""
    echo "Please re-run setup:"
    echo "  rm -rf venv && python3 setup.py"
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Verify activation worked by checking VIRTUAL_ENV is set
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate virtual environment"
    echo ""
    echo "Please try re-running setup:"
    echo "  rm -rf venv && python3 setup.py"
    exit 1
fi

# Check if start_buddy.py exists (created after full interactive setup)
if [ -f "$SCRIPT_DIR/start_buddy.py" ]; then
    echo "🤖 Starting Bit Buddy..."
    python "$SCRIPT_DIR/start_buddy.py" "$@"
else
    # Fallback to RAG server if no buddy configured yet
    echo "🤖 Starting Bit Buddy RAG Server..."
    echo "   (Run 'python3 setup.py' for full interactive setup with buddy creation)"
    echo ""
    uvicorn app.server:app --host 127.0.0.1 --port 8000 "$@"
fi
