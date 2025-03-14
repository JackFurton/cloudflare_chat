# Simple Chat Application

A simple real-time chat application built with Flask and Socket.IO that allows users to communicate across different networks using Cloudflare Tunnel.

## Features

- Real-time messaging
- Username-based identification
- User join/leave notifications
- Online users list
- Cross-network communication
- Easily accessible through Cloudflare Tunnel (Note: VPNs may interfere with Cloudflare connections)

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
- websocket-client for WebSocket support
- python-dotenv for environment variables
- cloudflared (installed separately via homebrew or direct download)

## Future Development Plans

- Image uploading capability
- Database for persistent chat history
- Multiple chat rooms
- User authentication

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

The app includes a sample configuration file (.env.example) with documentation for all available options. You can copy this file to customize app settings:

```bash
# Copy the example file
cp .env.example .env

# Edit with your preferred settings
nano .env  # or use any text editor
```

Available settings include:
- PORT: The server port (default: 5001)
- DEBUG: Enable/disable debug mode
- CORS_ORIGINS: Restrict allowed cross-origin requests
- SECRET_KEY: Custom secret key for Flask sessions

## Running the Chat Server

### Using the Helper Script

The simplest way to run the chat server is with the included script:

```bash
# Run with default settings
./run_chat.sh

# Change the port
./run_chat.sh --port 8080
```

### Using Python Directly

You can also run the server directly:

```bash
# Run with default settings
python run.py

# Specify a custom port
python run.py --port 8080
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

### Benefits of Using Cloudflare Tunnel

- Works through NATs (Note: Some VPNs may block Cloudflare connections)
- No port forwarding required
- Secure HTTPS connection
- Better reliability than ngrok
- No time limits or session restrictions

## Troubleshooting

### Installation Errors
- If cloudflared doesn't install properly, visit the [Cloudflare documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation) for detailed instructions
- If you see pip install errors, try updating pip: `pip install --upgrade pip`
- Make sure your Python version is 3.7 or higher

### Connection Problems
- If you see "Cannot connect to Cloudflare API", the most common fix is to **disable your VPN**
- VPNs often block Cloudflare connections, causing the tunnel creation to fail
- If not using a VPN, check your internet connection and firewall settings
- Ensure cloudflared is installed correctly and up-to-date
- If the tunnel connects but the chat doesn't work, check your browser console for errors

## Maintenance and Cleanup

The repository includes a `cleanup.sh` script that helps maintain your development environment. This script automatically runs when the server shuts down (via Ctrl+C or other termination).

The cleanup script performs the following tasks:
- Removes Python cache files (`__pycache__`, `.pyc`, `.pyo`, `.pyd`)
- Deletes the virtual environment (`venv/`)
- Cleans up log files
- Removes build artifacts (`build/`, `dist/`, `*.egg-info/`)

You don't need to manually run the cleanup script as it's automatically executed when you stop the server, but if needed, you can run it directly:

```bash
./cleanup.sh
```

## Security Notes

- This is a simple chat application with minimal security features
- The server accepts connections from any origin (`cors_allowed_origins="*"`)
- For personal/family use only, not recommended for sensitive communications
- Consider adding authentication for improved security if needed
- Cloudflare Tunnel provides secure HTTPS by default
