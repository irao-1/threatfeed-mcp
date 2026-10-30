#!/bin/bash
# ThreatFeed Setup Script

set -e

echo "🛡️ ThreatFeed Setup"
echo "=================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --quiet -r requirements.txt
echo "✅ Dependencies installed"

# Create data directory
mkdir -p data

# Initialize database
echo "🗄️ Initializing database..."
python3 src/aggregator.py --init
echo "✅ Database initialized"

# Fetch initial data
echo "🌐 Fetching initial threats..."
python3 src/aggregator.py --fetch
echo "✅ Initial data fetched"

# Show statistics
echo ""
echo "📊 Database Summary:"
python3 src/aggregator.py --stats

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start dashboard:  python3 src/dashboard.py"
echo "2. Start daemon:     python3 src/aggregator.py --daemon"
echo "3. View threats:     python3 src/aggregator.py --recent"
echo ""
echo "📖 See QUICKSTART.md for more information"
