"""
Tests for session manager
"""

from pyui_automation.core.services.session_manager import SessionManager


class TestSessionManager:
    """Test SessionManager class"""
    
    def test_init(self):
        """Test SessionManager initialization"""
        manager = SessionManager()
        assert manager is not None
    
    def test_create_session(self, mocker):
        """Test creating a session"""
        manager = SessionManager()
        mock_backend = mocker.Mock()
        mock_locator = mocker.Mock()
        
        session = manager.create_session(mock_backend, mock_locator)
        assert session is not None
    
    def test_get_session(self, mocker):
        """Test getting a session"""
        manager = SessionManager()
        mock_backend = mocker.Mock()
        mock_locator = mocker.Mock()
        
        session = manager.create_session(mock_backend, mock_locator)
        retrieved_session = manager.get_session(session.session_id)
        assert retrieved_session == session
    
    def test_close_session(self, mocker):
        """Test closing a session"""
        manager = SessionManager()
        mock_backend = mocker.Mock()
        mock_locator = mocker.Mock()
        
        session = manager.create_session(mock_backend, mock_locator)
        manager.close_session(session.session_id)
        
        # Session should be closed
        assert session.is_closed is True
    
    def test_get_nonexistent_session(self):
        """Test getting a non-existent session"""
        manager = SessionManager()
        
        session = manager.get_session("nonexistent")
        assert session is None 