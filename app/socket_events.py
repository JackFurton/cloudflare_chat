from flask import request
from flask_socketio import emit, join_room
from app import socketio
from typing import Dict, Set
import datetime

# Store active users
users: Dict[str, str] = {}  # session_id -> username
rooms: Dict[str, Set[str]] = {"global": set()}  # room_name -> set of session_ids

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
    
    # Get current time and format it
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    
    emit('user_joined', {'username': username}, room="global")
    emit('message', {
        'username': 'System',
        'message': f'{username} has joined the chat!',
        'timestamp': timestamp
    }, room="global")
    print(f"[{timestamp}] {username} joined")

@socketio.on('message')
def handle_message(data):
    if request.sid not in users:
        return
    
    username = users[request.sid]
    message = data.get('message')
    
    if message and message.strip() != "":
        # Get current time and format it
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        emit('message', {
            'username': username,
            'message': message,
            'timestamp': timestamp
        }, room="global")
        print(f"[{timestamp}] Message from {username}: {message}")