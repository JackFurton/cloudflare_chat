import sys
import os
import argparse
import atexit
import logging
from dotenv import load_dotenv
from app import app, socketio
from app.utils import setup_cloudflared, cleanup_tunnel

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('chat_app')

# Load environment variables
if os.path.exists('.env'):
    load_dotenv()

def main():
    """Main entry point for the chat application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the chat server')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 5001)),
                        help='Port to run the server on (default: 5001)')
    parser.add_argument('--debug', action='store_true', 
                        default=(os.environ.get('DEBUG', 'False').lower() == 'true'),
                        help='Run in debug mode')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host to bind the server to (default: 127.0.0.1)')
    parser.add_argument('--no-tunnel', action='store_true',
                        help='Run without setting up Cloudflare Tunnel')
    args = parser.parse_args()
    
    # Set secret key if provided
    if 'SECRET_KEY' in os.environ:
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    
    if not args.no_tunnel:
        try:
            # Set up Cloudflare Tunnel
            public_url = setup_cloudflared(args.port)
            app.config["BASE_URL"] = public_url
            atexit.register(cleanup_tunnel)
        except Exception as e:
            logger.error(f"Error setting up Cloudflare Tunnel: {e}")
            if "deadline exceeded" in str(e) or "timeout" in str(e):
                logger.error("Try disabling your VPN or check network connection")
            sys.exit(1)
        
        logger.info("\nNOTE: This chat app is ONLY accessible through the Cloudflare Tunnel URL above.")
    else:
        logger.info(f"\nRunning without Cloudflare Tunnel on http://{args.host}:{args.port}")
    
    # Start the Flask-SocketIO server
    socketio.run(app, host=args.host, port=args.port, 
                 debug=args.debug, log_output=False, use_reloader=False)

if __name__ == '__main__':
    main()