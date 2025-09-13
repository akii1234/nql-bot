"""
Database adapter for connecting to existing production databases
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseAdapter:
    """Adapter for connecting to existing production databases"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./data/movies.db")
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Field mappings for different database schemas
        self.field_mappings = self._get_field_mappings()
    
    def _get_field_mappings(self) -> Dict[str, Dict[str, str]]:
        """Define field mappings for different database schemas"""
        return {
            # Default mapping (our expected schema)
            "default": {
                "movie_id": "id",
                "title": "title",
                "release_date": "release_date",
                "genre": "genre",
                "director": "director",
                "cast": "cast",
                "rating": "rating",
                "plot_summary": "plot_summary",
                "duration_minutes": "duration_minutes",
                "language": "language",
                "country": "country"
            },
            
            # Example mapping for a different schema
            "alternative": {
                "movie_id": "movie_id",
                "title": "movie_title",
                "release_date": "release_year",  # If you have year instead of date
                "genre": "movie_genre",
                "director": "director_name",
                "cast": "actor_list",
                "rating": "imdb_rating",
                "plot_summary": "description",
                "duration_minutes": "runtime",
                "language": "original_language",
                "country": "production_country"
            }
        }
    
    def get_table_info(self) -> Dict[str, Any]:
        """Get information about existing tables in the database"""
        try:
            with self.engine.connect() as conn:
                # Get list of tables
                if "sqlite" in self.database_url:
                    tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
                elif "postgresql" in self.database_url:
                    tables_query = """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    """
                elif "mysql" in self.database_url:
                    tables_query = "SHOW TABLES"
                else:
                    tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
                
                result = conn.execute(text(tables_query))
                tables = [row[0] for row in result.fetchall()]
                
                # Get column info for each table
                table_info = {}
                for table in tables:
                    if "sqlite" in self.database_url:
                        columns_query = f"PRAGMA table_info({table})"
                        result = conn.execute(text(columns_query))
                        columns = [{"name": row[1], "type": row[2]} for row in result.fetchall()]
                    elif "postgresql" in self.database_url:
                        columns_query = """
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = %s
                        """
                        result = conn.execute(text(columns_query), (table,))
                        columns = [{"name": row[0], "type": row[1]} for row in result.fetchall()]
                    else:
                        columns = []
                    
                    table_info[table] = columns
                
                return {
                    "tables": tables,
                    "table_info": table_info
                }
                
        except Exception as e:
            print(f"Error getting table info: {e}")
            return {"tables": [], "table_info": {}}
    
    def detect_schema(self) -> str:
        """Automatically detect the database schema"""
        table_info = self.get_table_info()
        tables = table_info.get("tables", [])
        
        # Check for common table names
        if any("movie" in table.lower() for table in tables):
            # Check for specific field patterns
            for table in tables:
                if "movie" in table.lower():
                    columns = [col["name"].lower() for col in table_info["table_info"].get(table, [])]
                    
                    # Check for alternative schema patterns
                    if "movie_title" in columns or "movie_id" in columns:
                        return "alternative"
                    elif "title" in columns and "director" in columns:
                        return "default"
        
        return "default"
    
    def get_mapped_query(self, original_query: str, schema_type: str = None) -> str:
        """Convert a query to work with the existing database schema"""
        if not schema_type:
            schema_type = self.detect_schema()
        
        mappings = self.field_mappings.get(schema_type, self.field_mappings["default"])
        
        # Replace field names in the query
        mapped_query = original_query
        for expected_field, actual_field in mappings.items():
            if expected_field != actual_field:
                mapped_query = mapped_query.replace(f"m.{expected_field}", f"m.{actual_field}")
        
        return mapped_query
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a query and return results"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                columns = result.keys()
                rows = result.fetchall()
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False


def get_database_adapter() -> DatabaseAdapter:
    """Get database adapter instance"""
    return DatabaseAdapter()
