from flask import Flask
from flask_socketio import SocketIO

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-change-in-production'
socketio = SocketIO(app, cors_allowed_origins="*")

# Import routes after app creation to avoid circular imports
from app import routes, socket_events