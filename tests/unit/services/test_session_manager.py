"""
Tests for session manager
"""
import pytest
import time

from pyui_automation.services.session_manager import SessionManager
from pyui_automation.core.services.session import AutomationSession


class TestSessionManagerInitialization:
    """Test SessionManager initialization"""
    
    def test_session_manager_initialization(self, mocker):
        """Test basic initialization"""
        manager = SessionManager()
        assert manager is not None
        assert hasattr(manager, '_sessions')
        assert isinstance(manager._sessions, dict)


class TestSessionManagerCreateSession:
    """Test session creation"""
    
    def test_create_session_with_valid_params(self, mocker):
        """Test creating session with valid parameters"""
        manager = SessionManager()
        session = manager.create_session(mocker.Mock(), mocker.Mock())
        
        assert isinstance(session, AutomationSession)
        assert session.session_id is not None
        assert session.backend == mocker.Mock()
        assert session.locator == mocker.Mock()
    
    def test_create_session_with_custom_id(self, mocker):
        """Test creating session with custom ID"""
        manager = SessionManager()
        custom_id = "test_session_123"
        session = manager.create_session(mocker.Mock(), mocker.Mock(), custom_id)
        
        assert session.session_id == custom_id
        assert manager.get_session(custom_id) == session
    
    def test_create_session_with_existing_id(self, mocker):
        """Test creating session with existing ID returns existing session"""
        manager = SessionManager()
        session_id = "existing_session"
        
        # Create first session
        session1 = manager.create_session(mocker.Mock(), mocker.Mock(), session_id)
        
        # Create second session with same ID
        session2 = manager.create_session(mocker.Mock(), mocker.Mock(), session_id)
        
        assert session1 == session2
        assert manager.get_session_count() == 1


class TestSessionManagerGetSession:
    """Test session retrieval"""
    
    def test_get_session_with_existing_session(self, mocker):
        """Test getting existing session"""
        manager = SessionManager()
        session = manager.create_session(mocker.Mock(), mocker.Mock(), "test_session")
        
        retrieved_session = manager.get_session("test_session")
        assert retrieved_session == session
    
    def test_get_session_with_nonexistent_session(self):
        """Test getting nonexistent session"""
        manager = SessionManager()
        session = manager.get_session("nonexistent_session")
        assert session is None


class TestSessionManagerCloseSession:
    """Test session closing"""
    
    def test_close_session_with_existing_session(self, mocker):
        """Test closing existing session"""
        manager = SessionManager()
        session = manager.create_session(mocker.Mock(), mocker.Mock(), "test_session")
        
        # Mock cleanup method
        session.cleanup = mocker.Mock()
        
        manager.close_session("test_session")
        
        assert "test_session" not in manager._sessions
        session.cleanup.assert_called_once()
    
    def test_close_session_with_nonexistent_session(self):
        """Test closing nonexistent session"""
        manager = SessionManager()
        # Should not raise exception
        manager.close_session("nonexistent_session")
    
    def test_close_session_without_cleanup_method(self, mocker):
        """Test closing session without cleanup method"""
        manager = SessionManager()
        session = manager.create_session(mocker.Mock(), mocker.Mock(), "test_session")
        
        # Mock cleanup method to raise exception
        session.cleanup = mocker.Mock(side_effect=Exception("Cleanup failed"))
        
        # Should not raise exception
        manager.close_session("test_session")
        # Session remains in _sessions when cleanup fails
        assert "test_session" in manager._sessions


class TestSessionManagerCleanupAllSessions:
    """Test cleanup of all sessions"""
    
    def test_cleanup_all_sessions_with_multiple_sessions(self, mocker):
        """Test cleaning up multiple sessions"""
        manager = SessionManager()
        
        # Create multiple sessions
        session1 = manager.create_session(mocker.Mock(), mocker.Mock(), "session1")
        session2 = manager.create_session(mocker.Mock(), mocker.Mock(), "session2")
        
        # Mock cleanup methods
        session1.cleanup = mocker.Mock()
        session2.cleanup = mocker.Mock()
        
        manager.cleanup_all_sessions()
        
        assert len(manager._sessions) == 0
        session1.cleanup.assert_called_once()
        session2.cleanup.assert_called_once()
    
    def test_cleanup_all_sessions_with_no_sessions(self):
        """Test cleaning up with no sessions"""
        manager = SessionManager()
        manager.cleanup_all_sessions()
        assert len(manager._sessions) == 0


class TestSessionManagerGetActiveSessions:
    """Test getting active sessions"""
    
    def test_get_active_sessions_with_sessions(self, mocker):
        """Test getting active sessions when sessions exist"""
        manager = SessionManager()
        manager.create_session(mocker.Mock(), mocker.Mock(), "session1")
        manager.create_session(mocker.Mock(), mocker.Mock(), "session2")
        
        active_sessions = manager.get_active_sessions()
        assert "session1" in active_sessions
        assert "session2" in active_sessions
        assert len(active_sessions) == 2
    
    def test_get_active_sessions_with_no_sessions(self):
        """Test getting active sessions when no sessions exist"""
        manager = SessionManager()
        active_sessions = manager.get_active_sessions()
        assert active_sessions == []


class TestSessionManagerGetSessionCount:
    """Test getting session count"""
    
    def test_get_session_count_with_sessions(self, mocker):
        """Test getting session count when sessions exist"""
        manager = SessionManager()
        manager.create_session(mocker.Mock(), mocker.Mock(), "session1")
        manager.create_session(mocker.Mock(), mocker.Mock(), "session2")
        
        count = manager.get_session_count()
        assert count == 2
    
    def test_get_session_count_with_no_sessions(self):
        """Test getting session count when no sessions exist"""
        manager = SessionManager()
        count = manager.get_session_count()
        assert count == 0
    
    def test_get_session_count_with_exception(self, mocker):
        """Test getting session count with exception"""
        manager = SessionManager()
        manager.create_session(mocker.Mock(), mocker.Mock(), "session1")
        
        # Mock _sessions to raise exception
        with mocker.patch.object(manager, '_sessions', side_effect=Exception("Test error")):
            count = manager.get_session_count()
            assert count == 0


class TestSessionManagerIsSessionActive:
    """Test checking session activity"""
    
    def test_is_session_active_with_active_session(self, mocker):
        """Test checking active session"""
        manager = SessionManager()
        manager.create_session(mocker.Mock(), mocker.Mock(), "active_session")
        
        assert manager.is_session_active("active_session") is True
    
    def test_is_session_active_with_inactive_session(self):
        """Test checking inactive session"""
        manager = SessionManager()
        assert manager.is_session_active("inactive_session") is False


class TestSessionManagerGetSessionInfo:
    """Test getting session information"""
    
    def test_get_session_info_with_existing_session(self, mocker):
        """Test getting info for existing session"""
        manager = SessionManager()
        session = manager.create_session(mocker.Mock(), mocker.Mock(), "test_session")
        
        info = manager.get_session_info("test_session")
        
        assert info["exists"] is True
        assert info["session_id"] == "test_session"
        assert "backend" in info
        assert "locator" in info
        assert "config" in info
    
    def test_get_session_info_with_nonexistent_session(self):
        """Test getting info for nonexistent session"""
        manager = SessionManager()
        info = manager.get_session_info("nonexistent_session")
        assert info["exists"] is False
    
    def test_get_session_info_with_exception(self, mocker):
        """Test getting session info with exception"""
        manager = SessionManager()
        session = manager.create_session(mocker.Mock(), mocker.Mock(), "test_session")
        
        # Mock the _sessions dictionary to raise an exception when get() is called
        with mocker.patch.object(manager, '_sessions', {'test_session': session}):
            # Replace the dictionary with a mock that raises an exception
            manager._sessions = mocker.Mock()
            manager._sessions.get.side_effect = Exception("Test error")
            
            info = manager.get_session_info("test_session")
            assert info["exists"] is False
            assert "error" in info


class TestSessionManagerCleanup:
    """Test cleanup method"""
    
    def test_cleanup_method(self, mocker):
        """Test cleanup method"""
        manager = SessionManager()
        session = manager.create_session(mocker.Mock(), mocker.Mock(), "test_session")
        session.cleanup = mocker.Mock()
        
        manager.cleanup()
        
        assert len(manager._sessions) == 0
        session.cleanup.assert_called_once()
    
    def test_cleanup_method_with_exception(self, mocker):
        """Test cleanup method with exception"""
        manager = SessionManager()
        manager.create_session(mocker.Mock(), mocker.Mock(), "test_session")
        
        # Mock cleanup_all_sessions to raise exception
        with mocker.patch.object(manager, 'cleanup_all_sessions', side_effect=Exception("Test error")):
            # Should not raise exception
            manager.cleanup()


class TestSessionManagerIntegration:
    """Integration tests for SessionManager"""
    
    def test_session_lifecycle(self, mocker):
        """Test complete session lifecycle"""
        manager = SessionManager()
        
        # Create session
        session = manager.create_session(mocker.Mock(), mocker.Mock(), "lifecycle_session")
        assert manager.get_session_count() == 1
        assert manager.is_session_active("lifecycle_session") is True
        
        # Get session info
        info = manager.get_session_info("lifecycle_session")
        assert info["exists"] is True
        
        # Close session
        session.cleanup = mocker.Mock()
        manager.close_session("lifecycle_session")
        assert manager.get_session_count() == 0
        assert manager.is_session_active("lifecycle_session") is False
        
        # Get session info after closing
        info = manager.get_session_info("lifecycle_session")
        assert info["exists"] is False
    
    def test_multiple_sessions_management(self, mocker):
        """Test managing multiple sessions"""
        manager = SessionManager()
        
        # Create multiple sessions
        session1 = manager.create_session(mocker.Mock(), mocker.Mock(), "session1")
        session2 = manager.create_session(mocker.Mock(), mocker.Mock(), "session2")
        session3 = manager.create_session(mocker.Mock(), mocker.Mock(), "session3")
        
        assert manager.get_session_count() == 3
        assert len(manager.get_active_sessions()) == 3
        
        # Close one session
        session1.cleanup = mocker.Mock()
        manager.close_session("session1")
        
        assert manager.get_session_count() == 2
        assert "session1" not in manager.get_active_sessions()
        assert "session2" in manager.get_active_sessions()
        assert "session3" in manager.get_active_sessions()
        
        # Cleanup all sessions
        session2.cleanup = mocker.Mock()
        session3.cleanup = mocker.Mock()
        manager.cleanup_all_sessions()
        
        assert manager.get_session_count() == 0
        assert len(manager.get_active_sessions()) == 0


class TestSessionManagerErrorHandling:
    """Test error handling in SessionManager"""
    
    def test_create_session_with_exception_during_creation(self, mocker):
        """Test creating session with exception during creation"""
        manager = SessionManager()
        
        # Mock logger to raise exception
        with mocker.patch.object(manager._logger, 'info', side_effect=Exception("Logging failed")):
            with pytest.raises(Exception, match="Logging failed"):
                manager.create_session(mocker.Mock(), mocker.Mock(), "test_session")
    
    def test_get_session_with_exception_during_retrieval(self, mocker):
        """Test get_session when exception occurs during retrieval"""
        manager = SessionManager()
        session = manager.create_session(mocker.Mock(), mocker.Mock(), "test_session")
        
        # Mock the _sessions dictionary to raise an exception when get() is called
        with mocker.patch.object(manager, '_sessions', {'test_session': session}):
            # Replace the dictionary with a mock that raises an exception
            manager._sessions = mocker.Mock()
            manager._sessions.get.side_effect = Exception("Test error")
            
            # Should handle exception gracefully and return None
            session = manager.get_session("test_session")
            assert session is None

    def test_close_session_with_exception_during_closing(self, mocker):
        """Test close_session when exception occurs during closing"""
        manager = SessionManager()
        session = manager.create_session(mocker.Mock(), mocker.Mock(), "test_session")
        with mocker.patch.object(manager._logger, 'error', side_effect=Exception("Logging failed")):
            # Should handle exception gracefully and not re-raise
            manager.close_session("test_session")
            # No exception should be raised

    def test_cleanup_all_sessions_with_exception_during_cleanup(self, mocker):
        """Test cleanup_all_sessions when exception occurs during cleanup"""
        manager = SessionManager()
        manager.create_session(mocker.Mock(), mocker.Mock(), "session1")
        manager.create_session(mocker.Mock(), mocker.Mock(), "session2")
        with mocker.patch.object(manager._logger, 'error', side_effect=Exception("Logging failed")):
            # Should handle exception gracefully and not re-raise
            manager.cleanup_all_sessions()
            # No exception should be raised
    
    def test_get_active_sessions_with_exception(self, mocker):
        """Test getting active sessions with exception"""
        manager = SessionManager()
        manager.create_session(mocker.Mock(), mocker.Mock(), "session1")
        
        # Mock _sessions to raise exception
        with mocker.patch.object(manager, '_sessions', side_effect=Exception("Test error")):
            sessions = manager.get_active_sessions()
            assert sessions == []
    
    def test_get_session_count_with_exception(self, mocker):
        """Test getting session count with exception"""
        manager = SessionManager()
        manager.create_session(mocker.Mock(), mocker.Mock(), "session1")
        
        # Mock _sessions to raise exception
        with mocker.patch.object(manager, '_sessions', side_effect=Exception("Test error")):
            count = manager.get_session_count()
            assert count == 0
    
    def test_is_session_active_with_exception(self, mocker):
        """Test checking session activity with exception"""
        manager = SessionManager()
        manager.create_session(mocker.Mock(), mocker.Mock(), "session1")
        
        # Mock _sessions to raise exception
        with mocker.patch.object(manager, '_sessions', side_effect=Exception("Test error")):
            is_active = manager.is_session_active("session1")
            assert is_active is False
    
    def test_get_session_info_with_exception_during_info_retrieval(self, mocker):
        """Test getting session info with exception during info retrieval"""
        manager = SessionManager()
        session = manager.create_session(mocker.Mock(), mocker.Mock(), "test_session")
        
        # Mock the _sessions dictionary to raise an exception when get() is called
        with mocker.patch.object(manager, '_sessions', {'test_session': session}):
            # Replace the dictionary with a mock that raises an exception
            manager._sessions = mocker.Mock()
            manager._sessions.get.side_effect = Exception("Test error")
            
            # Should handle exception gracefully and return error info
            info = manager.get_session_info("test_session")
            assert info["exists"] is False
            assert "error" in info
    
    def test_cleanup_with_exception_during_cleanup(self, mocker):
        """Test cleanup with exception during cleanup"""
        manager = SessionManager()
        session = manager.create_session(mocker.Mock(), mocker.Mock(), "test_session")
        
        # Mock cleanup_all_sessions to raise exception
        with mocker.patch.object(manager, 'cleanup_all_sessions', side_effect=Exception("Cleanup failed")):
            # Should handle exception gracefully and log error
            manager.cleanup()
            # No exception should be raised
    
    def test_destructor_with_exception(self, mocker):
        """Test destructor with exception"""
        manager = SessionManager()
        session = manager.create_session(mocker.Mock(), mocker.Mock(), "test_session")
        
        # Mock cleanup to raise exception
        with mocker.patch.object(manager, 'cleanup', side_effect=Exception("Destructor failed")):
            # Destructor should not raise exception
            manager.__del__()


class TestSessionManagerEdgeCases:
    """Test edge cases in SessionManager"""
    
    def test_create_session_with_none_session_id(self, mocker):
        """Test creating session with None session ID"""
        manager = SessionManager()
        session = manager.create_session(mocker.Mock(), mocker.Mock(), None)
        assert session is not None
        assert manager.get_session_count() == 1
    
    def test_create_session_with_empty_session_id(self, mocker):
        """Test creating session with empty session ID"""
        manager = SessionManager()
        session = manager.create_session(mocker.Mock(), mocker.Mock(), "")
        assert session is not None
        assert manager.get_session_count() == 1
    
    def test_get_session_with_none_session_id(self, mocker):
        """Test getting session with None session ID"""
        manager = SessionManager()
        session = manager.get_session(None)
        assert session is None
    
    def test_get_session_with_empty_session_id(self, mocker):
        """Test getting session with empty session ID"""
        manager = SessionManager()
        session = manager.get_session("")
        assert session is None
    
    def test_close_session_with_none_session_id(self, mocker):
        """Test closing session with None session ID"""
        manager = SessionManager()
        # Should not raise exception
        manager.close_session(None)
    
    def test_close_session_with_empty_session_id(self, mocker):
        """Test closing session with empty session ID"""
        manager = SessionManager()
        # Should not raise exception
        manager.close_session("")
    
    def test_is_session_active_with_none_session_id(self, mocker):
        """Test checking session activity with None session ID"""
        manager = SessionManager()
        is_active = manager.is_session_active(None)
        assert is_active is False
    
    def test_is_session_active_with_empty_session_id(self, mocker):
        """Test checking session activity with empty session ID"""
        manager = SessionManager()
        is_active = manager.is_session_active("")
        assert is_active is False
    
    def test_get_session_info_with_none_session_id(self, mocker):
        """Test getting session info with None session ID"""
        manager = SessionManager()
        info = manager.get_session_info(None)
        assert info["exists"] is False
    
    def test_get_session_info_with_empty_session_id(self, mocker):
        """Test getting session info with empty session ID"""
        manager = SessionManager()
        info = manager.get_session_info("")
        assert info["exists"] is False 