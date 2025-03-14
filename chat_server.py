from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import os
import sys
import atexit
from typing import Dict, Set
from app.utils import setup_cloudflared, cleanup_tunnel

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store users and rooms
users: Dict[str, str] = {}  # session_id -> username
rooms: Dict[str, Set[str]] = {"global": set()}  # room_name -> set of session_ids

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in users:
        username = users[request.sid]
        del users[request.sid]
        # Remove user from all rooms
        for room in rooms.values():
            if request.sid in room:
                room.remove(request.sid)
        emit('user_left', {'username': username}, broadcast=True)
        print(f"{username} disconnected")

@socketio.on('join')
def handle_join(data):
    username = data.get('username')
    if not username or username.strip() == "":
        return
    
    users[request.sid] = username
    rooms["global"].add(request.sid)
    join_room("global")
    
    emit('user_joined', {'username': username}, room="global")
    emit('message', {
        'username': 'System',
        'message': f'{username} has joined the chat!'
    }, room="global")
    print(f"{username} joined")

@socketio.on('message')
def handle_message(data):
    if request.sid not in users:
        return
    
    username = users[request.sid]
    message = data.get('message')
    
    if message and message.strip() != "":
        emit('message', {
            'username': username,
            'message': message
        }, room="global")
        print(f"Message from {username}: {message}")

if __name__ == '__main__':
    # Parse arguments
    port = 5001
    if "--port" in sys.argv:
        port_index = sys.argv.index("--port") + 1
        if port_index < len(sys.argv):
            try:
                port = int(sys.argv[port_index])
            except ValueError:
                pass
    
    try:
        # Set up Cloudflare Tunnel
        public_url = setup_cloudflared(port)
        app.config["BASE_URL"] = public_url
        atexit.register(cleanup_tunnel)
    except Exception as e:
        print(f"Error setting up Cloudflare Tunnel: {e}")
        sys.exit(1)
    
    print("\nNOTE: This chat app is ONLY accessible through the Cloudflare Tunnel URL above.")
    
    # Start the server
    socketio.run(app, host='127.0.0.1', port=port, debug=True, 
                 log_output=False, use_reloader=False)
