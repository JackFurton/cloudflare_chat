# Simple Chat Application

A simple real-time chat application built with Flask and Socket.IO that allows users to communicate across different networks using Cloudflare Tunnel.

## Features

- Real-time messaging with timestamps
- Username-based identification
- User join/leave notifications
- Online users list
- Cross-network communication via Cloudflare Tunnel
- Connection status indicator
- Responsive design

## Project Structure

```
chat_app/
├── app/                    # Application package
│   ├── __init__.py         # Flask app initialization
│   ├── routes.py           # Web routes
│   ├── socket_events.py    # Socket.IO event handlers
│   ├── utils.py            # Utility functions (Cloudflare Tunnel setup)
│   └── templates/          # HTML templates
│       └── index.html      # Chat interface
├── run.py                  # Application entry point
├── run_chat.sh             # Helper script to run the application
└── requirements.txt        # Dependencies
```

## Requirements

- Python 3.7+ (compatible with Python 3.13)
- Flask and Flask-SocketIO for the web framework
- cloudflared (installed separately via homebrew or direct download)

## Installation and Setup

### 1. Install Cloudflared

This application uses Cloudflare Tunnel to create a secure public URL for your chat.

**On macOS:**
```bash
brew install cloudflared
```

**On Linux:**
Follow the instructions at https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation

### 2. Clone or download this repository

### 3. Optional: Create a .env file for configuration:

```bash
# Example .env file
PORT=5001
DEBUG=False
SECRET_KEY=your_custom_secret_key
```

## Running the Chat Server

### Using the Helper Script

The simplest way to run the chat server is with the included script:

```bash
# Make the script executable
chmod +x run_chat.sh

# Run with default settings
./run_chat.sh

# Change the port
./run_chat.sh --port 8080

# Run in debug mode
./run_chat.sh --debug

# Run without Cloudflare Tunnel (local only)
./run_chat.sh --no-tunnel
```

### Using Python Directly

You can also run the server directly:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with default settings
python run.py

# Specify a custom port
python run.py --port 8080

# Run without Cloudflare Tunnel
python run.py --no-tunnel
```

## How to Connect

1. Run the chat server:
   ```bash
   ./run_chat.sh
   ```

2. Look for the Cloudflare Tunnel URL in the console output:
   ```
   Cloudflare Tunnel URL: https://random-words.trycloudflare.com
   ```

3. Share this URL with your chat partner
   - They can simply open this URL in their browser
   - No port forwarding or special setup needed!
   - Note: You may need to disable VPN connections as they can block Cloudflare access

## Troubleshooting

### VPN Issues
- **Important**: VPNs often block Cloudflare connections, causing the tunnel creation to fail
- If you see "Cannot connect to Cloudflare API", the most common fix is to **disable your VPN**
- You can run without a tunnel using `--no-tunnel` to test locally

### Connection Problems
- If the tunnel connects but the chat doesn't work, check your browser console for errors
- Make sure your browser allows WebSocket connections
- Check that you're using the Cloudflare Tunnel URL rather than accessing via localhost

## Security Notes

- This is a simple chat application with minimal security features
- The server accepts connections from any origin (`cors_allowed_origins="*"`)
- For personal/family use only, not recommended for sensitive communications
- Cloudflare Tunnel provides secure HTTPS by default