"""
Session manager for handling user API keys and preferences
"""

import os
import secrets
import time
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import json
from pathlib import Path


class SessionManager:
    """Manages user sessions and API keys securely"""
    
    def __init__(self):
        self.sessions_dir = Path("data/sessions")
        self.sessions_dir.mkdir(exist_ok=True)
        self.session_timeout = 24 * 60 * 60  # 24 hours
    
    def create_session(self, user_name: str, ai_provider: str, api_key: str) -> str:
        """Create a new user session"""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            "session_id": session_id,
            "user_name": user_name,
            "ai_provider": ai_provider,
            "api_key": api_key,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "is_active": True
        }
        
        # Save session to file
        session_file = self.sessions_dir / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by session ID"""
        session_file = self.sessions_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is expired
            last_accessed = datetime.fromisoformat(session_data["last_accessed"])
            if datetime.now() - last_accessed > timedelta(seconds=self.session_timeout):
                self.delete_session(session_id)
                return None
            
            # Update last accessed time
            session_data["last_accessed"] = datetime.now().isoformat()
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            return session_data
            
        except Exception as e:
            print(f"Error reading session {session_id}: {e}")
            return None
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data"""
        session_data = self.get_session(session_id)
        if not session_data:
            return False
        
        session_data.update(updates)
        session_data["last_accessed"] = datetime.now().isoformat()
        
        session_file = self.sessions_dir / f"{session_id}.json"
        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error updating session {session_id}: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its data"""
        session_file = self.sessions_dir / f"{session_id}.json"
        try:
            if session_file.exists():
                session_file.unlink()
            return True
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.now()
        
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                last_accessed = datetime.fromisoformat(session_data["last_accessed"])
                if current_time - last_accessed > timedelta(seconds=self.session_timeout):
                    session_file.unlink()
                    print(f"Cleaned up expired session: {session_data.get('user_name', 'Unknown')}")
                    
            except Exception as e:
                print(f"Error cleaning up session file {session_file}: {e}")
    
    def get_user_environment(self, session_id: str) -> Optional[Dict[str, str]]:
        """Get environment variables for a user session"""
        session_data = self.get_session(session_id)
        if not session_data:
            return None
        
        return {
            "AI_PROVIDER": session_data["ai_provider"],
            "OPENAI_API_KEY": session_data["api_key"] if session_data["ai_provider"] == "openai" else "",
            "GEMINI_API_KEY": session_data["api_key"] if session_data["ai_provider"] == "gemini" else ""
        }
    
    def validate_api_key(self, ai_provider: str, api_key: str) -> bool:
        """Validate API key by making a test request"""
        try:
            if ai_provider == "openai":
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.1,
                    api_key=api_key
                )
                # Test with a simple request
                response = llm.invoke("Hello")
                return bool(response.content)
                
            elif ai_provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-exp",
                    temperature=0.1,
                    google_api_key=api_key
                )
                # Test with a simple request
                response = llm.invoke("Hello")
                return bool(response.content)
                
        except Exception as e:
            print(f"API key validation failed: {e}")
            return False
        
        return False


# Global session manager instance
session_manager = SessionManager()
