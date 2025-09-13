#!/usr/bin/env python3
"""
Test script for the session-based NQL Movie Chatbot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from backend.services.session_manager import session_manager

API_BASE_URL = "http://localhost:8000"

def test_session_system():
    """Test the complete session-based system"""
    print("🧪 Testing Session-Based NQL Movie Chatbot...")
    
    # Test 1: User Setup
    print("\n1️⃣ Testing User Setup...")
    setup_data = {
        "user_name": "Test User",
        "ai_provider": "openai",
        "api_key": "test-key-123"  # This will fail validation, but we can test the flow
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/setup/user-setup", json=setup_data)
        print(f"   Setup Response: {response.status_code}")
        
        if response.status_code == 400:
            print("   ✅ API key validation working (expected failure with test key)")
        else:
            print(f"   Response: {response.json()}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to API. Make sure server is running.")
        return False
    
    # Test 2: Session Management
    print("\n2️⃣ Testing Session Management...")
    
    # Create a test session manually
    session_id = session_manager.create_session(
        user_name="Test User",
        ai_provider="openai",
        api_key="test-key"
    )
    print(f"   ✅ Created test session: {session_id[:8]}...")
    
    # Test session retrieval
    session_data = session_manager.get_session(session_id)
    if session_data:
        print(f"   ✅ Session retrieved: {session_data['user_name']}")
    else:
        print("   ❌ Failed to retrieve session")
        return False
    
    # Test 3: Session Info API
    print("\n3️⃣ Testing Session Info API...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/setup/session-info/{session_id}")
        if response.status_code == 200:
            info = response.json()
            print(f"   ✅ Session info: {info['user_name']} using {info['ai_provider']}")
        else:
            print(f"   ❌ Session info failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Session info error: {e}")
    
    # Test 4: Logout
    print("\n4️⃣ Testing Logout...")
    try:
        response = requests.delete(f"{API_BASE_URL}/api/setup/logout/{session_id}")
        if response.status_code == 200:
            print("   ✅ Logout successful")
        else:
            print(f"   ❌ Logout failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Logout error: {e}")
    
    # Test 5: Session Cleanup
    print("\n5️⃣ Testing Session Cleanup...")
    session_manager.cleanup_expired_sessions()
    print("   ✅ Session cleanup completed")
    
    print("\n🎉 Session system tests completed!")
    return True

def test_with_real_api_key():
    """Test with a real API key (if provided)"""
    print("\n🔑 Testing with Real API Key...")
    
    # You can set these environment variables for testing
    api_key = os.getenv("TEST_OPENAI_API_KEY") or os.getenv("TEST_GEMINI_API_KEY")
    provider = "openai" if os.getenv("TEST_OPENAI_API_KEY") else "gemini"
    
    if not api_key:
        print("   ⚠️  No test API key found. Set TEST_OPENAI_API_KEY or TEST_GEMINI_API_KEY environment variable.")
        return True
    
    setup_data = {
        "user_name": "Real Test User",
        "ai_provider": provider,
        "api_key": api_key
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/setup/user-setup", json=setup_data)
        
        if response.status_code == 200:
            data = response.json()
            session_id = data["session_id"]
            print(f"   ✅ Real API key setup successful: {session_id[:8]}...")
            
            # Test a query
            query_data = {
                "query": "Find me the highest rated movies",
                "session_id": session_id
            }
            
            query_response = requests.post(f"{API_BASE_URL}/api/queries/process", json=query_data)
            if query_response.status_code == 200:
                result = query_response.json()
                print(f"   ✅ Query processed successfully: {len(result.get('results', []))} results")
            else:
                print(f"   ❌ Query failed: {query_response.status_code}")
            
            # Cleanup
            requests.delete(f"{API_BASE_URL}/api/setup/logout/{session_id}")
            print("   ✅ Cleanup completed")
            
        else:
            error_data = response.json()
            print(f"   ❌ Real API key setup failed: {error_data.get('detail', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ❌ Real API key test error: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Session System Tests...")
    
    success = test_session_system()
    
    if success:
        test_with_real_api_key()
    
    print("\n✅ All tests completed!")
    sys.exit(0 if success else 1)
