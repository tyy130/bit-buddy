#!/bin/bash
# Codespaces setup script for Bit Buddy development environment

set -e

echo "🚀 Setting up Bit Buddy development environment in Codespaces..."

# Update system
sudo apt-get update

# Install Python development dependencies
echo "📦 Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Install development tools
pip install pytest pytest-asyncio pytest-cov
pip install black isort flake8 mypy
pip install jupyter notebook

# Install optional AI dependencies (lightweight versions)
echo "🧠 Installing AI dependencies (CPU versions for development)..."
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
pip install chromadb

# Create workspace directories
echo "📁 Setting up workspace directories..."
mkdir -p /workspaces/data/{buddies,test-data,debug-logs}

# Create sample test files
echo "📄 Creating sample test files..."
mkdir -p /workspaces/data/test-data/sample-files
cat > /workspaces/data/test-data/sample-files/ai-research.txt << 'EOF'
# AI Research Notes

This document contains information about artificial intelligence and machine learning.
The buddy should be able to find this when searching for AI-related content.

## Topics Covered
- Neural networks
- Deep learning  
- Natural language processing
- Computer vision

Last updated: $(date)
EOF

cat > /workspaces/data/test-data/sample-files/project-ideas.md << 'EOF'
# Project Ideas

## Web Development
- Personal portfolio website
- E-commerce platform
- Blog with AI integration

## AI Projects  
- Chatbot development
- Image classification
- Text summarization

## File Organization
- Automated file sorting
- Duplicate detection
- Content analysis

Created for Bit Buddy testing.
EOF

cat > /workspaces/data/test-data/sample-files/python-script.py << 'EOF'
#!/usr/bin/env python3
"""
Sample Python script for testing code file detection
"""

import os
import json
from pathlib import Path

def main():
    print("Hello from a Python script!")
    
    # Sample code that a buddy might analyze
    files = list(Path(".").glob("*.txt"))
    print(f"Found {len(files)} text files")

if __name__ == "__main__":
    main()
EOF

# Set up Git configuration for the codespace
echo "🔧 Configuring Git..."
git config --global user.name "Codespace User"
git config --global user.email "user@codespace.local"

# Create helpful aliases
echo "⚡ Setting up aliases..."
cat >> ~/.bashrc << 'EOF'

# Bit Buddy Development Aliases
alias bb-test="python tools/test_runner.py"
alias bb-debug="python tools/debug_tools.py"
alias bb-deploy="python tools/deploy.py"
alias bb-setup="python setup.py"
alias bb-health="python tools/deploy.py health"

# Quick test commands
alias test-unit="python tools/test_runner.py --unit --verbose"
alias test-integration="python tools/test_runner.py --integration --verbose" 
alias test-all="python tools/test_runner.py --all --verbose"

# Development helpers
alias serve-docs="python -m http.server 8080"
alias buddy-logs="tail -f /workspaces/data/debug-logs/*.log"

echo "🤖 Bit Buddy development environment ready!"
echo "💡 Try these commands:"
echo "  • bb-test --unit     - Run unit tests"
echo "  • bb-health          - Check system health"  
echo "  • bb-setup           - Interactive setup"
echo "  • bb-debug monitor   - Performance monitoring"
EOF

# Make workspace data directory writable
chmod -R 755 /workspaces/data

# Run initial health check
echo "🏥 Running initial health check..."
python -c "
try:
    import sys
    print(f'✅ Python {sys.version}')
    
    # Test imports
    import fastapi
    print('✅ FastAPI imported')
    
    import watchdog
    print('✅ Watchdog imported')
    
    import requests
    print('✅ Requests imported')
    
    # Test our modules
    from debug_tools import BitBuddyDebugger
    print('✅ Debug tools imported')
    
    from enhanced_buddy import EnhancedBitBuddy
    print('✅ Enhanced buddy imported')
    
    print()
    print('🎉 All core dependencies available!')
    print('🚀 Ready for Bit Buddy development!')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

echo "✅ Codespace setup complete!"
echo ""
echo "🎯 Next steps:"
echo "  1. Run 'bb-test --unit' to verify everything works"
echo "  2. Try 'bb-setup' for interactive buddy creation"
echo "  3. Use 'bb-health' to check system status"
echo "  4. Open ports 8000-8003 for buddy servers"
echo ""
echo "📖 See README.md for full documentation"
echo "🐛 Use 'bb-debug' for troubleshooting"