"""
Session Manager - handles session lifecycle management.

Responsible for:
- Session creation
- Session tracking
- Session cleanup
- Session retrieval
"""

import uuid
from typing import Dict, Optional, List, Any, override
from logging import getLogger

from .session import AutomationSession
from ..interfaces.isession_manager import ISessionManager


class SessionManager(ISessionManager):
    """Manager for automation sessions"""
    
    def __init__(self):
        self._logger = getLogger(__name__)
        self._sessions: Dict[str, AutomationSession] = {}
    
    @override
    def create_session(self, backend: Any, locator: Any, session_id: Optional[str] = None) -> "AutomationSession":
        """Create a new automation session"""
        try:
            if session_id is None:
                session_id = f"session_{uuid.uuid4().hex[:8]}"
            
            if session_id in self._sessions:
                self._logger.warning(f"Session {session_id} already exists, returning existing session")
                return self._sessions[session_id]
            
            session = AutomationSession(session_id, backend, {"locator": locator})
            self._sessions[session_id] = session
            self._logger.info(f"Created automation session: {session_id}")
            
            return session
        except Exception as e:
            self._logger.error(f"Failed to create session {session_id}: {e}")
            raise
    
    @override
    def get_session(self, session_id: str) -> Optional["AutomationSession"]:
        """Get existing session by ID"""
        try:
            session = self._sessions.get(session_id)
            if session:
                self._logger.debug(f"Retrieved session: {session_id}")
            else:
                self._logger.warning(f"Session not found: {session_id}")
            return session
        except Exception as e:
            self._logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    def close_session(self, session_id: str) -> None:
        """Close and cleanup session"""
        try:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                if hasattr(session, 'cleanup'):
                    session.cleanup()
                del self._sessions[session_id]
                self._logger.info(f"Closed automation session: {session_id}")
            else:
                self._logger.warning(f"Session not found for closing: {session_id}")
        except Exception as e:
            self._logger.error(f"Failed to close session {session_id}: {e}")
    
    @override
    def cleanup_all_sessions(self) -> None:
        """Close all active sessions"""
        try:
            session_ids = list(self._sessions.keys())
            closed_count = 0
            
            for session_id in session_ids:
                if self.close_session(session_id):
                    closed_count += 1
            
            self._logger.info(f"Closed {closed_count} sessions")
        except Exception as e:
            self._logger.error(f"Failed to close all sessions: {e}")
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        try:
            return list(self._sessions.keys())
        except Exception as e:
            self._logger.error(f"Failed to get active sessions: {e}")
            return []
    
    def get_session_count(self) -> int:
        """Get number of active sessions"""
        try:
            return len(self._sessions)
        except Exception as e:
            self._logger.error(f"Failed to get session count: {e}")
            return 0
    
    def is_session_active(self, session_id: str) -> bool:
        """Check if session is active"""
        try:
            return session_id in self._sessions
        except Exception as e:
            self._logger.error(f"Failed to check session status {session_id}: {e}")
            return False
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about session"""
        try:
            session = self._sessions.get(session_id)
            if not session:
                return {"exists": False}
            
            return {
                "exists": True,
                "session_id": session_id,
                "backend": type(session.backend).__name__,
                "locator": type(session.locator).__name__,
                "config": str(session.config)
            }
        except Exception as e:
            self._logger.error(f"Failed to get session info {session_id}: {e}")
            return {"exists": False, "error": str(e)}
    
    def cleanup(self) -> None:
        """Cleanup all sessions"""
        try:
            self.cleanup_all_sessions()
            self._logger.info("SessionManager cleanup completed")
        except Exception as e:
            self._logger.error(f"Error during SessionManager cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup()
        except Exception:
            pass 