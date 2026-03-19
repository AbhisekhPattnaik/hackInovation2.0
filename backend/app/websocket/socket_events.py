"""Socket.io event handlers"""
from .socket_manager import socket_manager
from jose import jwt, JWTError
from ..auth import SECRET_KEY, ALGORITHM

async def handle_connect(sid, environ, auth):
    """Handle new socket connection"""
    print(f"\n🔗 Socket connection attempt: {sid}")
    print(f"Auth token received: {bool(auth)}")
    
    if not auth:
        print(f"❌ No auth provided for connection {sid}")
        return False
    
    try:
        # Extract token from auth header or auth dict
        token = auth.get('token') if isinstance(auth, dict) else auth
        
        if not token:
            print(f"❌ No token found in auth")
            return False
        
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get('user_id') or payload.get('sub')
        role = payload.get('role')
        
        if not user_id:
            print(f"❌ No user_id in token")
            return False
        
        print(f"✅ Socket authenticated for user {user_id} ({role})")
        
        # Store user data in session
        user_data = {
            'user_id': int(user_id),
            'role': role,
            'token': token
        }
        
        # Update user info with doctor/patient IDs if available
        if role == 'doctor':
            user_data['doctor_id'] = int(user_id)
        elif role == 'patient':
            user_data['patient_id'] = int(user_id)
        
        socket_manager.connect_user(sid, user_data)
        return True
        
    except JWTError as e:
        print(f"❌ JWT decode error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Auth error: {str(e)}")
        return False


async def handle_disconnect(sid):
    """Handle socket disconnection"""
    print(f"\n🔌 Socket disconnected: {sid}")
    user_data = socket_manager.get_user_by_sid(sid)
    if user_data:
        socket_manager.disconnect_user(user_data['user_id'])


async def handle_join_doctor_room(sid, data):
    """Handle doctor joining their room"""
    user_data = socket_manager.get_user_by_sid(sid)
    if user_data and user_data['role'] == 'doctor':
        doctor_id = data.get('doctor_id')
        socket_manager.join_doctor_room(doctor_id, sid)
        print(f"📋 Doctor {doctor_id} joined their queue room")
        return {'status': 'success', 'message': 'Joined doctor room'}
    return {'status': 'error', 'message': 'Unauthorized'}


async def handle_join_patient_room(sid, data):
    """Handle patient joining their room"""
    user_data = socket_manager.get_user_by_sid(sid)
    if user_data and user_data['role'] == 'patient':
        patient_id = data.get('patient_id')
        socket_manager.join_patient_room(patient_id, sid)
        print(f"👥 Patient {patient_id} joined their appointment room")
        return {'status': 'success', 'message': 'Joined patient room'}
    return {'status': 'error', 'message': 'Unauthorized'}


async def handle_queue_update(sid, data):
    """Handle queue update event"""
    user_data = socket_manager.get_user_by_sid(sid)
    if user_data and user_data['role'] == 'doctor':
        doctor_id = data.get('doctor_id')
        appointments = data.get('appointments', [])
        socket_manager.update_queue(doctor_id, appointments)
        print(f"✅ Queue updated: {len(appointments)} appointments for doctor {doctor_id}")
        return {'status': 'success'}
    return {'status': 'error', 'message': 'Unauthorized'}


async def handle_appointment_completed(sid, data):
    """Handle appointment completion notification"""
    user_data = socket_manager.get_user_by_sid(sid)
    if user_data and user_data['role'] == 'doctor':
        appointment_id = data.get('appointment_id')
        patient_id = data.get('patient_id')
        doctor_id = data.get('doctor_id')
        
        print(f"✅ Appointment {appointment_id} completed by doctor {doctor_id}")
        
        # Notify doctor room about completion
        doctor_sids = socket_manager.get_doctor_room_sids(doctor_id)
        print(f"📢 Broadcasting to {len(doctor_sids)} doctor connections")
        
        return {
            'status': 'success',
            'broadcast_to': len(doctor_sids),
            'notification': {
                'event': 'appointment_completed',
                'appointment_id': appointment_id,
                'patient_id': patient_id
            }
        }
    
    return {'status': 'error', 'message': 'Unauthorized'}


async def handle_appointment_booked(sid, data):
    """Handle appointment booking notification"""
    user_data = socket_manager.get_user_by_sid(sid)
    if user_data and user_data['role'] == 'patient':
        doctor_id = data.get('doctor_id')
        appointment_id = data.get('appointment_id')
        
        print(f"📅 New appointment {appointment_id} booked with doctor {doctor_id}")
        
        # Notify doctor room about new booking
        doctor_sids = socket_manager.get_doctor_room_sids(doctor_id)
        print(f"📢 Notifying {len(doctor_sids)} doctor connections")
        
        return {
            'status': 'success',
            'broadcast_to': len(doctor_sids),
            'notification': {
                'event': 'new_appointment',
                'appointment_id': appointment_id,
                'doctor_id': doctor_id
            }
        }
    
    return {'status': 'error', 'message': 'Unauthorized'}


async def handle_ping(sid, data):
    """Handle ping keep-alive"""
    return {'status': 'pong', 'timestamp': str(__import__('datetime').datetime.now())}
