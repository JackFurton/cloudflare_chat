from flask import request
from flask_socketio import emit, join_room
from app import socketio
from typing import Dict, Set
import datetime
from dataclasses import dataclass

# Store active users
users: Dict[str, str] = {}  # session_id -> username
rooms: Dict[str, Set[str]] = {"global": set()}  # room_name -> set of session_ids

@dataclass
class ChatMessage:
    """Represents a chat message."""
    username: str
    message: str
    timestamp: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert ChatMessage to dictionary for JSON serialization."""
        return {
            'username': self.username,
            'message': self.message,
            'timestamp': self.timestamp
        }

def get_timestamp() -> str:
    """Get current time formatted as HH:MM:SS."""
    return datetime.datetime.now().strftime("%H:%M:%S")

def create_system_message(message: str) -> ChatMessage:
    """Create a system message with the current timestamp."""
    return ChatMessage(
        username="System",
        message=message,
        timestamp=get_timestamp()
    )

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    if request.sid in users:
        username = users[request.sid]
        del users[request.sid]
        
        # Remove user from all rooms
        for room in rooms.values():
            if request.sid in room:
                room.remove(request.sid)
                
        # Notify other users
        emit('user_left', {'username': username}, broadcast=True)
        
        # Send system message
        system_msg = create_system_message(f'{username} has left the chat')
        emit('message', system_msg.to_dict(), room="global")
        
        print(f"[{get_timestamp()}] {username} disconnected")

@socketio.on('join')
def handle_join(data):
    """Handle user joining the chat."""
    username = data.get('username')
    if not username or username.strip() == "":
        return
    
    users[request.sid] = username
    rooms["global"].add(request.sid)
    join_room("global")
    
    timestamp = get_timestamp()
    
    # Notify about new user
    emit('user_joined', {'username': username}, room="global")
    
    # Send system message
    system_msg = create_system_message(f'{username} has joined the chat!')
    emit('message', system_msg.to_dict(), room="global")
    
    print(f"[{timestamp}] {username} joined")

@socketio.on('message')
def handle_message(data):
    """Handle incoming chat message."""
    if request.sid not in users:
        return
    
    username = users[request.sid]
    message = data.get('message')
    
    if message and message.strip() != "":
        timestamp = get_timestamp()
        
        # Create and send message
        chat_msg = ChatMessage(username=username, message=message, timestamp=timestamp)
        emit('message', chat_msg.to_dict(), room="global")
        
        print(f"[{timestamp}] Message from {username}: {message}")

@socketio.on('get_users')
def handle_get_users():
    """Send the list of active users to the requesting client."""
    active_users = list(users.values())
    emit('user_list', {'users': active_users})