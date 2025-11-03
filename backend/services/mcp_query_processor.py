"""
MCP (Model Context Protocol) Query Processor
Uses MCP to give LLM direct, structured access to the database
"""

import os
import json
from typing import Dict, Any, List, Optional
from sqlalchemy import text, inspect
from sqlalchemy.orm import sessionmaker

from backend.utils.database import engine
from backend.models.movie import Movie, MovieViewership

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class MCPQueryProcessor:
    """Query processor using Model Context Protocol for database access"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.db_session = SessionLocal()
        
        # Get session data for API key
        from backend.services.session_manager import session_manager
        self.session_data = session_manager.get_session(session_id)
        
        if not self.session_data:
            raise ValueError("Invalid or expired session")
        
        # Initialize LLM
        self.llm = self._initialize_llm()
        
        # Get database schema dynamically
        self.schema_info = self._get_database_schema()
    
    def _initialize_llm(self):
        """Initialize the appropriate LLM based on the AI provider"""
        ai_provider = self.session_data["ai_provider"]
        api_key = self.session_data["api_key"]
        
        if ai_provider == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1,
                openai_api_key=api_key
            )
        elif ai_provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                temperature=0.1,
                google_api_key=api_key
            )
        else:
            raise ValueError(f"Unsupported AI provider: {ai_provider}")
    
    def _get_database_schema(self) -> Dict[str, Any]:
        """Dynamically get database schema information using MCP approach"""
        inspector = inspect(engine)
        schema_info = {}
        
        for table_name in inspector.get_table_names():
            columns = []
            for column in inspector.get_columns(table_name):
                columns.append({
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column.get("nullable", True)
                })
            schema_info[table_name] = columns
        
        return schema_info
    
    def _format_schema_for_prompt(self) -> str:
        """Format database schema for LLM prompt"""
        schema_text = "Database Schema:\n\n"
        
        for table_name, columns in self.schema_info.items():
            schema_text += f"Table: {table_name}\n"
            for col in columns:
                nullable = "NULL" if col["nullable"] else "NOT NULL"
                schema_text += f"  - {col['name']} ({col['type']}) {nullable}\n"
            schema_text += "\n"
        
        return schema_text
    
    def _get_sample_data(self, table_name: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get sample data from a table for context"""
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            result = self.db_session.execute(text(query))
            
            columns = result.keys()
            rows = result.fetchall()
            
            samples = []
            for row in rows:
                row_dict = {}
                for i, column in enumerate(columns):
                    row_dict[column] = row[i]
                samples.append(row_dict)
            
            return samples
        except:
            return []
    
    def execute_sql(self, sql_query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        try:
            result = self.db_session.execute(text(sql_query))
            
            columns = result.keys()
            rows = result.fetchall()
            
            results = []
            for row in rows:
                row_dict = {}
                for i, column in enumerate(columns):
                    row_dict[column] = row[i]
                results.append(row_dict)
            
            return results
        except Exception as e:
            print(f"SQL execution error: {e}")
            return []
    
    def is_conversational(self, query: str) -> bool:
        """Check if query is conversational"""
        import re
        query_lower = query.lower().strip()
        
        conversational_patterns = [
            r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
            r'\b(how are you|how do you do|what\'s up|sup)\b',
            r'\b(what\'s your name|who are you)\b',
            r'\b(help|what can you do|what do you do)\b'
        ]
        
        for pattern in conversational_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def get_conversational_response(self, query: str) -> str:
        """Generate conversational response"""
        import re
        query_lower = query.lower().strip()
        
        if re.search(r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b', query_lower):
            return f"Hello {self.session_data['user_name']}! 👋 I'm your NQL Movie Chatbot. I have access to your movie database and can answer any questions about it!"
        
        elif re.search(r'\b(how are you|how do you do|what\'s up)\b', query_lower):
            return "I'm doing great, thank you! 😊 I'm ready to help you explore your movie database. What would you like to know?"
        
        elif re.search(r'\b(what\'s your name|who are you)\b', query_lower):
            return "I'm your NQL Movie Chatbot! 🎬 I use the Model Context Protocol (MCP) to directly access and query your movie database."
        
        elif re.search(r'\b(help|what can you do|what do you do)\b', query_lower):
            return f"""🎬 **I'm your MCP-powered Movie Chatbot!**

I have direct access to your movie database with {len(self.schema_info)} tables.

**What I can do:**
- Answer any question about your movies
- Generate and execute SQL queries automatically
- Provide insights and analytics
- Handle complex queries naturally

Just ask me anything about your movies in natural language! 🚀"""
        
        return "I'm here to help you with your movie database! What would you like to know?"
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process query using MCP approach"""
        try:
            # Handle conversational messages
            if self.is_conversational(query):
                return {
                    "sql_query": "",
                    "results": [],
                    "answer": self.get_conversational_response(query),
                    "success": True,
                    "is_conversational": True
                }
            
            # MCP APPROACH: Give LLM full context about the database
            schema_text = self._format_schema_for_prompt()
            
            # Get sample data for context
            sample_movies = self._get_sample_data("movies", limit=2)
            
            # Create MCP-style prompt with full database context
            from langchain_core.messages import SystemMessage, HumanMessage
            
            messages = [
                SystemMessage(content=f"""You are a database assistant with direct access to a movie database.

{schema_text}

Sample Data (movies table):
{json.dumps(sample_movies, indent=2, default=str)}

Your task:
Generate ONLY the SQL query needed to answer the user's question.

Important rules:
- Use the exact table and column names shown in the schema above
- For date queries, use proper date comparisons
- For aggregations, use appropriate GROUP BY and ORDER BY
- Always include LIMIT to prevent large result sets (unless counting)
- Return ONLY the SQL query, nothing else
- Do NOT wrap in JSON or markdown code blocks
- Do NOT include explanations or comments

Example:
User: "How many movies do you have?"
Response: SELECT COUNT(*) FROM movies

User: "Show me action movies from 2024"
Response: SELECT * FROM movies WHERE genre='Action' AND CAST(release_date AS DATE) >= '2024-01-01' AND CAST(release_date AS DATE) <= '2024-12-31' LIMIT 20
"""),
                HumanMessage(content=f"User question: {query}")
            ]
            
            # Get LLM response
            response = self.llm.invoke(messages)
            
            # Parse response - expecting just SQL
            response_content = response.content.strip()
            
            # Clean up response
            sql_query = response_content
            
            # Remove markdown code blocks if present
            if sql_query.startswith("```"):
                lines = sql_query.split("\n")
                # Remove first and last lines (markdown markers)
                if len(lines) > 2:
                    sql_query = "\n".join(lines[1:-1])
                    # Remove language identifier if present (e.g., "sql")
                    if sql_query.startswith("sql"):
                        sql_query = sql_query[3:].strip()
            
            # If LLM returned JSON despite instructions, extract the SQL
            if sql_query.strip().startswith("{"):
                try:
                    json_data = json.loads(sql_query)
                    sql_query = json_data.get("sql_query", "")
                    if not sql_query:
                        sql_query = json_data.get("query", response_content)
                except:
                    # If JSON parsing fails, return error
                    return {
                        "sql_query": "",
                        "results": [],
                        "answer": "Sorry, the AI returned an invalid response format. Please try rephrasing your question.",
                        "success": False
                    }
            
            sql_query = sql_query.strip()
            
            # Execute SQL
            results = self.execute_sql(sql_query)
            
            # Generate natural language answer
            answer = self._generate_answer(query, sql_query, results)
            
            return {
                "sql_query": sql_query,
                "results": results,
                "answer": answer,
                "success": True,
                "is_conversational": False
            }
            
        except Exception as e:
            print(f"MCP query processing error: {e}")
            return {
                "sql_query": "",
                "results": [],
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "success": False
            }
    
    def _generate_answer(self, query: str, sql_query: str, results: List[Dict]) -> str:
        """Generate natural language answer based on results"""
        if not results:
            return "I couldn't find any results matching your criteria. Try a different query!"
        
        # Handle count queries
        first_result = results[0]
        if len(results) == 1 and any(key.upper().startswith("COUNT") or key == "total_movies" for key in first_result.keys()):
            count = list(first_result.values())[0]
            return f"🎬 I found **{count}** movies in the database."
        
        # Handle regular queries
        if len(results) == 1:
            movie = results[0]
            if movie.get("title"):
                return f"I found: **{movie['title']}** ({movie.get('genre', 'Unknown genre')}, {movie.get('rating', 'N/A')}/10)"
        
        # Multiple results
        return f"I found {len(results)} results. Here's what I discovered based on your query!"
    
    def __del__(self):
        """Cleanup database session"""
        if hasattr(self, 'db_session'):
            self.db_session.close()


# Note: This is the new MCP-based approach
# The old approaches are kept in other files for reference
