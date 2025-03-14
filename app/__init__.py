from flask import Flask
from flask_socketio import SocketIO
import os

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
socketio = SocketIO(app, cors_allowed_origins="*")

# Import routes after app creation to avoid circular imports
from app import routes, socket_events