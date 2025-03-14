#!/bin/bash
echo "Starting cleanup..."

# Kill any remaining Cloudflare process
echo "Checking for running Cloudflare Tunnel processes..."
CLOUDFLARE_PID=$(pgrep -f "cloudflared.*tunnel")
if [ ! -z "$CLOUDFLARE_PID" ]; then
    echo "Terminating Cloudflare Tunnel process ($CLOUDFLARE_PID)..."
    kill -15 $CLOUDFLARE_PID 2>/dev/null || true
    
    # Give it a moment to terminate gracefully
    sleep 1
    
    # If still running, force kill
    if ps -p $CLOUDFLARE_PID > /dev/null; then
        echo "Force killing Cloudflare Tunnel process..."
        kill -9 $CLOUDFLARE_PID 2>/dev/null || true
    fi
fi

# Remove Python cache files
echo "Removing Python cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "*.pyd" -delete
find . -name ".pytest_cache" -type d -exec rm -rf {} +

# Create a fresh venv next time, don't remove the existing one
# echo "Removing virtual environment..."
# rm -rf venv

# Remove logs
echo "Removing log files..."
find . -name "*.log" -delete

# Remove build artifacts
echo "Removing build artifacts..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

echo "Cleanup complete!"