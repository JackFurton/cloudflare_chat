#!/bin/bash
echo "Starting cleanup..."

# Remove Python cache files
echo "Removing Python cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "*.pyd" -delete
find . -name ".pytest_cache" -type d -exec rm -rf {} +

# Remove virtual environment
echo "Removing virtual environment..."
rm -rf venv

# Remove logs
echo "Removing log files..."
find . -name "*.log" -delete

# Remove build artifacts
echo "Removing build artifacts..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# No need to clean up Cloudflare Tunnel files

echo "Cleanup complete!"