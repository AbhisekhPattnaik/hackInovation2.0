"""Socket.io event handlers and WebSocket management"""
import json
from typing import Dict, Set, List
from datetime import datetime

class SocketManager:
    """Manage Socket.io connections and events"""
    
    def __init__(self):
        # Store connected users: {user_id: {doctor_id, patient_id, role, sid}}
        self.connected_users = {}
        
        # Store doctor rooms: {doctor_id: [patient_sids]}
        self.doctor_rooms = {}
        
        # Store patient rooms: {patient_id: [sid]}
        self.patient_rooms = {}
        
        # Store active queues: {doctor_id: [appointment_ids]}
        self.active_queues = {}
    
    def connect_user(self, sid: str, user_data: dict):
        """Register a connected user"""
        user_id = user_data.get('user_id')
        self.connected_users[user_id] = {
            'sid': sid,
            'role': user_data.get('role'),
            'user_id': user_id,
            'doctor_id': user_data.get('doctor_id'),
            'patient_id': user_data.get('patient_id'),
            'connected_at': datetime.now().isoformat()
        }
        print(f"✅ User {user_id} ({user_data.get('role')}) connected with SID: {sid}")
    
    def disconnect_user(self, user_id: int):
        """Unregister a disconnected user"""
        if user_id in self.connected_users:
            del self.connected_users[user_id]
            print(f"❌ User {user_id} disconnected")
    
    def get_user_by_sid(self, sid: str) -> dict:
        """Get user info by socket session ID"""
        for user_id, user_data in self.connected_users.items():
            if user_data['sid'] == sid:
                return user_data
        return None
    
    def join_doctor_room(self, doctor_id: int, sid: str):
        """Add a user to a doctor's room (for real-time queue updates)"""
        if doctor_id not in self.doctor_rooms:
            self.doctor_rooms[doctor_id] = []
        if sid not in self.doctor_rooms[doctor_id]:
            self.doctor_rooms[doctor_id].append(sid)
        print(f"✅ SID {sid} joined doctor room {doctor_id}")
    
    def join_patient_room(self, patient_id: int, sid: str):
        """Add a user to a patient's room (for appointment updates)"""
        if patient_id not in self.patient_rooms:
            self.patient_rooms[patient_id] = []
        if sid not in self.patient_rooms[patient_id]:
            self.patient_rooms[patient_id].append(sid)
        print(f"✅ SID {sid} joined patient room {patient_id}")
    
    def leave_doctor_room(self, doctor_id: int, sid: str):
        """Remove user from doctor room"""
        if doctor_id in self.doctor_rooms and sid in self.doctor_rooms[doctor_id]:
            self.doctor_rooms[doctor_id].remove(sid)
            print(f"❌ SID {sid} left doctor room {doctor_id}")
    
    def leave_patient_room(self, patient_id: int, sid: str):
        """Remove user from patient room"""
        if patient_id in self.patient_rooms and sid in self.patient_rooms[patient_id]:
            self.patient_rooms[patient_id].remove(sid)
            print(f"❌ SID {sid} left patient room {patient_id}")
    
    def get_doctor_room_sids(self, doctor_id: int) -> List[str]:
        """Get all socket IDs in a doctor's room"""
        return self.doctor_rooms.get(doctor_id, [])
    
    def get_patient_room_sids(self, patient_id: int) -> List[str]:
        """Get all socket IDs in a patient's room"""
        return self.patient_rooms.get(patient_id, [])
    
    def update_queue(self, doctor_id: int, appointments: list):
        """Update queue for a doctor"""
        self.active_queues[doctor_id] = appointments
        print(f"📊 Queue updated for doctor {doctor_id}: {len(appointments)} appointments")
    
    def get_queue(self, doctor_id: int) -> list:
        """Get current queue for a doctor"""
        return self.active_queues.get(doctor_id, [])


# Global socket manager instance
socket_manager = SocketManager()
