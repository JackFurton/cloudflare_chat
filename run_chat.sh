#!/bin/bash

# Simple script to set up and run the chat server with Cloudflare Tunnel

# Function to run cleanup when script exits
cleanup() {
    echo "Server stopped, running cleanup..."
    # Deactivate virtual environment before cleanup
    deactivate
    # Run the cleanup script
    ./cleanup.sh
}

# Set up trap to catch exits and run cleanup
trap cleanup EXIT

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --port)
      PORT="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# Set default port if not specified
if [ -z "$PORT" ]; then
  PORT=5001
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it first."
    exit 1
fi

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "cloudflared is not installed. Please install it first."
    echo "macOS: brew install cloudflared"
    echo "Linux: Visit https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Start the chat server
echo "Starting chat server with Cloudflare Tunnel..."
echo "This will create a public URL you can share"
echo "NOTE: The chat is ONLY accessible through Cloudflare Tunnel, not directly via local IP"
echo "IMPORTANT: If you're using a VPN, you may need to disable it as VPNs can block Cloudflare connections"
python run.py --port $PORT
