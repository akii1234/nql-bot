#!/usr/bin/env python3
"""
Production setup script for NQL Movie Chatbot
"""

import sys
import os
import json
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from production.adapters.database_adapter import DatabaseAdapter
from dotenv import load_dotenv

def setup_production():
    """Setup production environment"""
    print("🚀 Setting up NQL Movie Chatbot for Production...")
    
    # Check if production config exists
    prod_config = project_root / "production" / "config" / "production.env"
    if not prod_config.exists():
        print("❌ Production config not found!")
        print("   Please copy production/config/production.env to .env and configure it")
        return False
    
    # Load environment
    load_dotenv(prod_config)
    
    # Test database connection
    print("\n🔍 Testing database connection...")
    db_adapter = DatabaseAdapter()
    
    if not db_adapter.test_connection():
        print("❌ Database connection failed!")
        print("   Please check your DATABASE_URL in the .env file")
        return False
    
    print("✅ Database connection successful!")
    
    # Analyze database schema
    print("\n📊 Analyzing database schema...")
    table_info = db_adapter.get_table_info()
    schema_type = db_adapter.detect_schema()
    
    print(f"   Schema Type: {schema_type}")
    print(f"   Tables Found: {len(table_info.get('tables', []))}")
    
    # Display schema information
    for table, columns in table_info.get("table_info", {}).items():
        print(f"   📁 {table}: {len(columns)} columns")
    
    # Test sample queries
    print("\n🧪 Testing sample queries...")
    test_queries = [
        "SELECT COUNT(*) as total_movies FROM movies",
        "SELECT * FROM movies LIMIT 3"
    ]
    
    for query in test_queries:
        try:
            results = db_adapter.execute_query(query)
            print(f"   ✅ {query} -> {len(results)} results")
        except Exception as e:
            print(f"   ❌ {query} -> Error: {e}")
    
    # Create production startup script
    create_production_scripts()
    
    print("\n🎉 Production setup completed!")
    print("\n📋 Next steps:")
    print("   1. Update your .env file with production settings")
    print("   2. Run: python production/scripts/start_production.py")
    print("   3. Test with: python production/scripts/test_production.py")
    
    return True

def create_production_scripts():
    """Create production-specific scripts"""
    scripts_dir = project_root / "production" / "scripts"
    
    # Create start_production.py
    start_script = scripts_dir / "start_production.py"
    start_script.write_text('''#!/usr/bin/env python3
"""
Production startup script
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Load production environment
from dotenv import load_dotenv
load_dotenv(project_root / "production" / "config" / "production.env")

# Import and run the main application
from main import app
import uvicorn

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting NQL Movie Chatbot in Production Mode...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Environment: Production")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
''')
    
    # Create test_production.py
    test_script = scripts_dir / "test_production.py"
    test_script.write_text('''#!/usr/bin/env python3
"""
Production testing script
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Load production environment
from dotenv import load_dotenv
load_dotenv(project_root / "production" / "config" / "production.env")

from production.adapters.production_query_processor import ProductionQueryProcessor

def test_production():
    """Test production setup"""
    print("🧪 Testing Production Setup...")
    
    try:
        # Initialize production processor
        processor = ProductionQueryProcessor()
        print("✅ Production query processor initialized")
        
        # Get database info
        db_info = processor.get_database_info()
        print(f"✅ Database connection: {db_info['connection_status']}")
        print(f"✅ Schema type: {db_info['schema_type']}")
        
        # Test a sample query
        test_query = "Find me the highest rated movies"
        print(f"🔍 Testing query: '{test_query}'")
        
        intent = processor.parse_query(test_query)
        results = processor.execute_query(intent)
        
        print(f"✅ Query executed successfully! Found {len(results)} results")
        
        if results:
            print("📋 Sample results:")
            for i, result in enumerate(results[:3], 1):
                print(f"   {i}. {result.get('title', 'Unknown')} - Rating: {result.get('rating', 'N/A')}")
        
        print("\\n🎉 Production setup is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_production()
    sys.exit(0 if success else 1)
''')
    
    # Make scripts executable
    os.chmod(start_script, 0o755)
    os.chmod(test_script, 0o755)
    
    print("✅ Production scripts created")

if __name__ == "__main__":
    success = setup_production()
    sys.exit(0 if success else 1)
