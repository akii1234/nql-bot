"""
Production-ready query processor that works with existing databases
"""

from backend.services.query_processor import NQLQueryProcessor, QueryIntent
from backend.utils.database_adapter import DatabaseAdapter
from typing import List, Dict, Any
import os


class ProductionQueryProcessor(NQLQueryProcessor):
    """Production query processor that adapts to existing database schemas"""
    
    def __init__(self):
        super().__init__()
        self.db_adapter = DatabaseAdapter()
        self.schema_type = self.db_adapter.detect_schema()
        
        # Update system prompt based on detected schema
        self._update_system_prompt()
    
    def _update_system_prompt(self):
        """Update system prompt based on actual database schema"""
        table_info = self.db_adapter.get_table_info()
        tables = table_info.get("tables", [])
        
        # Build schema description
        schema_description = "Available tables and fields:\n"
        for table, columns in table_info.get("table_info", {}).items():
            schema_description += f"- {table}: {', '.join([col['name'] for col in columns])}\n"
        
        # Update the system prompt
        self.system_prompt = f"""
        You are a Natural Query Language (NQL) processor for a movie database system.
        Your job is to parse natural language queries about movies and convert them into structured data.

        {schema_description}

        Common query patterns:
        1. "Find movies most watched between [date1] and [date2]" -> intent: aggregate, aggregation: most_watched, time_range: {{start, end}}
        2. "Show me action movies from 2024" -> intent: filter, filters: {{genre: "action", release_date: "2024"}}
        3. "What are the highest rated movies?" -> intent: aggregate, aggregation: highest_rated
        4. "Find movies by Christopher Nolan" -> intent: filter, filters: {{director: "Christopher Nolan"}}

        Always respond with valid JSON in this exact format:
        {{
            "intent_type": "search|filter|aggregate|compare",
            "entities": ["list", "of", "extracted", "entities"],
            "filters": {{
                "genre": "action",
                "director": "Christopher Nolan",
                "rating_min": 8.0,
                "release_year": 2024
            }},
            "aggregation": "most_watched|highest_rated|most_recent|longest|shortest",
            "time_range": {{
                "start": "2025-01-01",
                "end": "2025-02-03"
            }}
        }}
        """
    
    def generate_sql_query(self, intent: QueryIntent) -> str:
        """Generate SQL query adapted to the existing database schema"""
        # Get the base query from parent class
        base_query = super().generate_sql_query(intent)
        
        # Adapt the query to the existing schema
        adapted_query = self.db_adapter.get_mapped_query(base_query, self.schema_type)
        
        return adapted_query
    
    def execute_query(self, intent: QueryIntent) -> List[Dict[str, Any]]:
        """Execute query against the production database"""
        try:
            # Generate SQL query
            sql_query = self.generate_sql_query(intent)
            
            # Execute against production database
            results = self.db_adapter.execute_query(sql_query)
            
            return results
            
        except Exception as e:
            print(f"Error executing production query: {e}")
            return []
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the production database"""
        return {
            "connection_status": self.db_adapter.test_connection(),
            "schema_type": self.schema_type,
            "table_info": self.db_adapter.get_table_info(),
            "field_mappings": self.db_adapter.field_mappings.get(self.schema_type, {})
        }
