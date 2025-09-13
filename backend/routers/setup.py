from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time

from backend.services.session_manager import session_manager

router = APIRouter(prefix="/api/setup", tags=["setup"])


class UserSetupRequest(BaseModel):
    user_name: str
    ai_provider: str  # "openai" or "gemini"
    api_key: str


class UserSetupResponse(BaseModel):
    session_id: str
    user_name: str
    ai_provider: str
    setup_successful: bool
    message: str


class SessionInfo(BaseModel):
    session_id: str
    user_name: str
    ai_provider: str
    is_valid: bool
    created_at: str
    last_accessed: str


@router.post("/user-setup", response_model=UserSetupResponse)
async def setup_user(request: UserSetupRequest):
    """Setup user with API key and preferences"""
    try:
        # Validate input
        if not request.user_name.strip():
            raise HTTPException(status_code=400, detail="User name is required")
        
        if request.ai_provider not in ["openai", "gemini"]:
            raise HTTPException(status_code=400, detail="AI provider must be 'openai' or 'gemini'")
        
        if not request.api_key.strip():
            raise HTTPException(status_code=400, detail="API key is required")
        
        # Validate API key
        print(f"Validating {request.ai_provider} API key...")
        is_valid = session_manager.validate_api_key(request.ai_provider, request.api_key)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid API key. Please check your key and try again.")
        
        # Create session
        session_id = session_manager.create_session(
            user_name=request.user_name,
            ai_provider=request.ai_provider,
            api_key=request.api_key
        )
        
        return UserSetupResponse(
            session_id=session_id,
            user_name=request.user_name,
            ai_provider=request.ai_provider,
            setup_successful=True,
            message=f"Welcome {request.user_name}! Your {request.ai_provider} API key has been validated and saved securely."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")


@router.get("/session-info/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """Get information about a session"""
    session_data = session_manager.get_session(session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    return SessionInfo(
        session_id=session_id,
        user_name=session_data["user_name"],
        ai_provider=session_data["ai_provider"],
        is_valid=True,
        created_at=session_data["created_at"],
        last_accessed=session_data["last_accessed"]
    )


@router.post("/validate-session/{session_id}")
async def validate_session(session_id: str):
    """Validate if a session is still active"""
    session_data = session_manager.get_session(session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    return {
        "valid": True,
        "user_name": session_data["user_name"],
        "ai_provider": session_data["ai_provider"]
    }


@router.delete("/logout/{session_id}")
async def logout_user(session_id: str):
    """Logout user and delete session"""
    success = session_manager.delete_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "message": "Logged out successfully. Your API key has been securely removed.",
        "success": True
    }


@router.post("/cleanup-sessions")
async def cleanup_expired_sessions():
    """Clean up expired sessions (admin endpoint)"""
    session_manager.cleanup_expired_sessions()
    
    return {
        "message": "Expired sessions cleaned up successfully",
        "success": True
    }
