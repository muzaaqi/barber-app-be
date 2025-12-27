from flask import request
from flask_socketio import join_room
from app.extensions import socketio

@socketio.on('connect')
def handle_connect():
    print(f"CLIENT CONNECTED: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"CLIENT DISCONNECTED: {request.sid}")

@socketio.on('join_room')
def handle_join_room(room):
    join_room(room)
    print(f"Client {request.sid} joined room: {room}")