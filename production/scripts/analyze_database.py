#!/usr/bin/env python3
"""
Script to analyze existing production database and suggest field mappings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.database_adapter import DatabaseAdapter
from dotenv import load_dotenv

load_dotenv()

def analyze_database():
    """Analyze the existing database and suggest configurations"""
    print("🔍 Analyzing your production database...")
    
    # Initialize database adapter
    db_adapter = DatabaseAdapter()
    
    # Test connection
    if not db_adapter.test_connection():
        print("❌ Cannot connect to database. Please check your DATABASE_URL in .env file")
        return
    
    print("✅ Database connection successful!")
    
    # Get database information
    table_info = db_adapter.get_table_info()
    schema_type = db_adapter.detect_schema()
    
    print(f"\n📊 Database Analysis Results:")
    print(f"   Schema Type: {schema_type}")
    print(f"   Total Tables: {len(table_info.get('tables', []))}")
    
    # Display tables and their columns
    print(f"\n📋 Tables and Columns:")
    for table, columns in table_info.get("table_info", {}).items():
        print(f"   📁 {table}:")
        for col in columns:
            print(f"      - {col['name']} ({col['type']})")
    
    # Suggest field mappings
    print(f"\n🔧 Suggested Field Mappings:")
    mappings = db_adapter.field_mappings.get(schema_type, {})
    
    if schema_type == "default":
        print("   ✅ Your database schema matches our expected format!")
    else:
        print("   ⚠️  Your database schema differs from our expected format.")
        print("   📝 Suggested mappings:")
        for expected_field, actual_field in mappings.items():
            if expected_field != actual_field:
                print(f"      {expected_field} -> {actual_field}")
    
    # Generate configuration recommendations
    print(f"\n⚙️  Configuration Recommendations:")
    print("   1. Update your .env file with the correct DATABASE_URL")
    print("   2. If your schema differs, update the field mappings in database_adapter.py")
    print("   3. Test the connection with: uv run python scripts/test_production_db.py")
    
    # Sample queries to test
    print(f"\n🧪 Sample Queries to Test:")
    sample_queries = [
        "SELECT COUNT(*) FROM movies",
        "SELECT * FROM movies LIMIT 5",
        "SELECT genre, COUNT(*) FROM movies GROUP BY genre"
    ]
    
    for query in sample_queries:
        try:
            results = db_adapter.execute_query(query)
            print(f"   ✅ {query} -> {len(results)} results")
        except Exception as e:
            print(f"   ❌ {query} -> Error: {e}")

if __name__ == "__main__":
    analyze_database()
