#!/usr/bin/env python3
"""
Script to test API connection and query processing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.query_processor import NQLQueryProcessor
from dotenv import load_dotenv

load_dotenv()

def test_api_connection():
    """Test the API connection and basic query processing"""
    print("🧪 Testing API Connection...")
    
    try:
        # Initialize the query processor
        processor = NQLQueryProcessor()
        print(f"✅ Successfully initialized {processor.ai_provider.upper()} API")
        
        # Test a simple query
        test_query = "Find me the movies which was most watched between 01-01-2025 to 03-02-2025"
        print(f"🔍 Testing query: '{test_query}'")
        
        # Parse the query
        intent = processor.parse_query(test_query)
        print("✅ Query parsed successfully!")
        print(f"   Intent Type: {intent.intent_type}")
        print(f"   Aggregation: {intent.aggregation}")
        print(f"   Time Range: {intent.time_range}")
        
        # Generate SQL query
        sql_query = processor.generate_sql_query(intent)
        print("✅ SQL query generated successfully!")
        print(f"   SQL: {sql_query}")
        
        print("\n🎉 All tests passed! Your API is working correctly.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure your .env file exists and contains the correct API key")
        print("2. For Gemini: Set GEMINI_API_KEY=your_key and AI_PROVIDER=gemini")
        print("3. For OpenAI: Set OPENAI_API_KEY=your_key and AI_PROVIDER=openai")
        print("4. Check your internet connection")
        return False
    
    return True

if __name__ == "__main__":
    success = test_api_connection()
    sys.exit(0 if success else 1)
