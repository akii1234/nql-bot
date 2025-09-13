"""
Session-aware query processor that uses user's API keys
"""

from backend.services.query_processor import NQLQueryProcessor, QueryIntent
from backend.services.session_manager import session_manager
from typing import Optional, Dict, Any
import os


class SessionQueryProcessor(NQLQueryProcessor):
    """Query processor that uses session-specific API keys"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.session_data = session_manager.get_session(session_id)
        
        if not self.session_data:
            raise ValueError("Invalid or expired session")
        
        # Set up environment variables for this session
        self._setup_session_environment()
        
        # Initialize the parent class
        super().__init__()
    
    def _setup_session_environment(self):
        """Set up environment variables for this session"""
        env_vars = session_manager.get_user_environment(self.session_id)
        if env_vars:
            for key, value in env_vars.items():
                os.environ[key] = value
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get user information from session"""
        return {
            "user_name": self.session_data["user_name"],
            "ai_provider": self.session_data["ai_provider"],
            "session_created": self.session_data["created_at"],
            "last_accessed": self.session_data["last_accessed"]
        }
    
    def is_session_valid(self) -> bool:
        """Check if the session is still valid"""
        return session_manager.get_session(self.session_id) is not None
    
    def refresh_session(self):
        """Refresh the session to update last accessed time"""
        self.session_data = session_manager.get_session(self.session_id)
        if self.session_data:
            self._setup_session_environment()
    
    def logout(self):
        """Logout and clean up session"""
        session_manager.delete_session(self.session_id)
        self.session_data = None
