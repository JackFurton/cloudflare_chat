#!/bin/bash

# Simple script to set up and run the chat server with Cloudflare Tunnel

# Function to run cleanup when script exits
cleanup() {
    echo "Server stopped, running cleanup..."
    # Deactivate virtual environment before cleanup
    deactivate 2>/dev/null || true
    # Run the cleanup script if it exists
    if [ -f "./cleanup.sh" ]; then
        ./cleanup.sh
    fi
}

# Set up trap to catch exits and run cleanup
trap cleanup EXIT

# Parse command line arguments
PORT=5001
DEBUG=false
NO_TUNNEL=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --port)
      PORT="$2"
      shift 2
      ;;
    --debug)
      DEBUG=true
      shift
      ;;
    --no-tunnel)
      NO_TUNNEL=true
      shift
      ;;
    *)
      shift
      ;;
  esac
done

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it first."
    exit 1
fi

# Check if cloudflared is installed (only if using tunnel)
if [ "$NO_TUNNEL" = false ] && ! command -v cloudflared &> /dev/null; then
    echo "cloudflared is not installed. Please install it first."
    echo "macOS: brew install cloudflared"
    echo "Linux: Visit https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation"
    echo ""
    echo "Alternatively, run with --no-tunnel to skip Cloudflare Tunnel setup."
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
pip install -q -r requirements.txt

# Build command
CMD="python run.py --port $PORT"

if [ "$DEBUG" = true ]; then
    CMD="$CMD --debug"
fi

if [ "$NO_TUNNEL" = true ]; then
    CMD="$CMD --no-tunnel"
    echo "Starting chat server WITHOUT Cloudflare Tunnel..."
    echo "The chat will be accessible locally at http://127.0.0.1:$PORT"
else
    echo "Starting chat server with Cloudflare Tunnel..."
    echo "This will create a public URL you can share"
    echo "NOTE: The chat is ONLY accessible through Cloudflare Tunnel, not directly via local IP"
    echo "IMPORTANT: If you're using a VPN, you may need to disable it as VPNs can block Cloudflare connections"
fi

# Start the chat server
$CMD