import sys
import os
import argparse
import atexit
from dotenv import load_dotenv
from app import app, socketio
from app.utils import setup_cloudflared, cleanup_tunnel

# Load environment variables
if os.path.exists('.env'):
    load_dotenv()

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the chat server')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 5001)))
    parser.add_argument('--debug', action='store_true', 
                        default=(os.environ.get('DEBUG', 'True').lower() == 'true'))
    args = parser.parse_args()
    
    # Set secret key if provided
    if 'SECRET_KEY' in os.environ:
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    
    try:
        # Set up Cloudflare Tunnel
        public_url = setup_cloudflared(args.port)
        app.config["BASE_URL"] = public_url
        atexit.register(cleanup_tunnel)
    except Exception as e:
        print(f"Error setting up Cloudflare Tunnel: {e}")
        if "deadline exceeded" in str(e) or "timeout" in str(e):
            print("\nTry disabling your VPN or check network connection")
        sys.exit(1)
    
    print("\nNOTE: This chat app is ONLY accessible through the Cloudflare Tunnel URL above.")
    
    # Start the Flask-SocketIO server
    socketio.run(app, host='127.0.0.1', port=args.port, 
                 debug=args.debug, log_output=False, use_reloader=False)
