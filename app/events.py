from flask import request
from flask_socketio import emit, join_room
from app.extensions import socketio

@socketio.on('connect')
def handle_connect():
    print(f"[V] CLIENT CONNECTED: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[X] CLIENT DISCONNECTED: {request.sid}")

@socketio.on('join_user_room')
def handle_join_user_room(data):
    user_id = data.get('user_id')
    if user_id:
        room_name = f"user_{user_id}"
        join_room(room_name)
        print(f"[->] User {user_id} joined room: {room_name}")
        emit('room_joined', {'message': f"Joined room {room_name}"}, to=room_name)