"""
Session management for UI automation.
"""

from typing import Dict, Any
import logging

from ..interfaces.iapplication import IApplication


class AutomationSession:
    """Represents an automation session with application and configuration."""
    
    def __init__(self, session_id: str, application: IApplication, config: Dict[str, Any]) -> None:
        self.session_id = session_id
        self.application = application
        self.config = config
        self.backend = application
        self.locator = config.get("locator")
        self.logger = logging.getLogger(f"session.{session_id}")
        self.is_closed = False
        
    def get_session_id(self) -> str:
        """Get the session ID."""
        return self.session_id
        
    def get_application(self) -> IApplication:
        """Get the application instance."""
        return self.application
        
    def get_config(self) -> Dict[str, Any]:
        """Get the session configuration."""
        return self.config
        
    def cleanup(self) -> None:
        """Cleanup session resources."""
        self.logger.info(f"Cleaning up session: {self.session_id}")
        # Add cleanup logic here if needed 
        
    def close(self) -> None:
        """Close session"""
        self.is_closed = True 