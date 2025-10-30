#!/bin/bash
# cleanup.sh - Stop all running services and clean build artifacts

echo "🧹 Cleaning up Bit Buddy workspace..."

# Kill any running servers
echo "  Stopping servers..."
pkill -f "uvicorn app.server" 2>/dev/null && echo "    ✓ Stopped uvicorn" || echo "    - No uvicorn running"
pkill -f "buddy_gui.py" 2>/dev/null && echo "    ✓ Stopped GUI" || echo "    - No GUI running"

# Clean build artifacts
echo "  Removing build artifacts..."
rm -rf build/ dist/ *.egg-info/ .pytest_cache/ __pycache__/ 2>/dev/null
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Clean temporary files
echo "  Removing temporary files..."
rm -f /tmp/server.log 2>/dev/null

echo "✅ Cleanup complete!"
echo ""
echo "Active processes:"
ps aux | grep -E "(uvicorn|python.*buddy)" | grep -v grep || echo "  (none)"
