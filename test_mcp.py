#!/usr/bin/env python3
"""
Test MCP Query Processor
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.mcp_query_processor import MCPQueryProcessor
from backend.services.session_manager import session_manager

def test_mcp():
    """Test MCP query processor"""
    print("🧪 Testing MCP Query Processor...")
    
    # Create a test session
    session_id = session_manager.create_session(
        user_name="Test User",
        ai_provider="gemini",
        api_key="test-key"
    )
    
    try:
        # Initialize MCP processor
        processor = MCPQueryProcessor(session_id)
        
        print("\n✅ MCP Processor initialized")
        print(f"📊 Detected {len(processor.schema_info)} tables:")
        for table_name, columns in processor.schema_info.items():
            print(f"   - {table_name}: {len(columns)} columns")
        
        # Test schema formatting
        schema_text = processor._format_schema_for_prompt()
        print(f"\n📝 Schema formatted for LLM:")
        print(schema_text[:500] + "...")
        
        # Test sample data
        sample_movies = processor._get_sample_data("movies", limit=2)
        print(f"\n🎬 Sample movies retrieved: {len(sample_movies)} rows")
        if sample_movies:
            print(f"   First movie: {sample_movies[0].get('title', 'Unknown')}")
        
        print("\n🎉 MCP setup is working correctly!")
        
    finally:
        # Cleanup
        session_manager.delete_session(session_id)

if __name__ == "__main__":
    test_mcp()
