#!/bin/bash

# TTNN Web Calculator Startup Script

echo "🚀 Starting TTNN Web Calculator..."

# Navigate to tt-metal and activate environment
cd /home/aswin/tt-metal
if [ ! -f "python_env/bin/activate" ]; then
    echo "❌ Python environment not found at /home/aswin/tt-metal/python_env"
    exit 1
fi

source python_env/bin/activate
echo "✅ Python environment activated"

# Navigate to web calculator directory
cd /home/aswin/ttnn-web-calculator

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing Flask..."
    pip install Flask==3.0.0
fi

# Start the application
echo "🌐 Starting Flask server..."
echo "📍 Open your browser and navigate to: http://localhost:5000"
echo ""
python app.py
