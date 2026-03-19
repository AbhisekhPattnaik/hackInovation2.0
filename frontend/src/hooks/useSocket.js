import { useEffect, useRef, useCallback } from 'react';
import io from 'socket.io-client';

const SOCKET_URL = 'http://localhost:8000';

/**
 * Custom hook for managing Socket.io connection
 * @param {string} room - Room to join (e.g., 'doctor_123' or 'patient_456')
 * @param {function} onEvent - Callback for socket events
 * @returns {object} Socket instance methods
 */
export const useSocket = (room, eventHandlers = {}) => {
  const socketRef = useRef(null);
  const isConnectingRef = useRef(false);

  const connect = useCallback(() => {
    if (socketRef.current?.connected || isConnectingRef.current) {
      console.log('ℹ️ Socket already connected or connecting');
      return;
    }

    isConnectingRef.current = true;
    const token = localStorage.getItem('token');

    try {
      socketRef.current = io(SOCKET_URL, {
        auth: {
          token: token
        },
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: 5,
        transports: ['websocket', 'polling']
      });

      // Connection events
      socketRef.current.on('connect', () => {
        console.log('✅ Socket connected:', socketRef.current.id);
        isConnectingRef.current = false;
        
        // Join room if specified
        if (room) {
          console.log(`🚪 Joining room: ${room}`);
          socketRef.current.emit('join_room', { room });
        }
      });

      socketRef.current.on('connect_error', (error) => {
        console.error('❌ Socket connection error:', error);
        isConnectingRef.current = false;
      });

      socketRef.current.on('disconnect', (reason) => {
        console.log('🔌 Socket disconnected:', reason);
      });

      // Register custom event handlers
      Object.entries(eventHandlers).forEach(([event, handler]) => {
        if (socketRef.current) {
          socketRef.current.on(event, handler);
          console.log(`📡 Registered handler for: ${event}`);
        }
      });

    } catch (error) {
      console.error('Failed to initialize socket:', error);
      isConnectingRef.current = false;
    }
  }, [room, eventHandlers]);

  const emit = useCallback((event, data) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit(event, data);
      console.log(`📤 Emitted event: ${event}`, data);
    } else {
      console.warn('⚠️ Socket not connected, cannot emit:', event);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      console.log('🔌 Socket disconnected manually');
    }
  }, []);

  const isConnected = useCallback(() => {
    return socketRef.current?.connected ?? false;
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      if (socketRef.current?.connected) {
        socketRef.current.disconnect();
      }
    };
  }, [connect]);

  return {
    emit,
    disconnect,
    isConnected,
    socket: socketRef.current
  };
};

export default useSocket;
