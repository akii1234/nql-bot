"""
Direct LLM Query Processor - Simple approach where LLM directly generates SQL and answers
This is the new approach that works like ChatGPT but with database access
"""

import os
import json
import re
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from backend.utils.database import engine
from backend.models.movie import Movie, MovieViewership

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DirectQueryProcessor:
    """Direct LLM processor that generates SQL and answers naturally"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id
        self.ai_provider = None
        self.llm = None
        
        # Database schema information for the LLM
        self.schema_info = """
        Database Schema:
        
        Table: movies
        - id (INTEGER, PRIMARY KEY)
        - title (TEXT)
        - release_date (DATE)
        - genre (TEXT) - values: Action, Comedy, Drama, Horror, Sci-Fi, Romance, Thriller, Adventure, Fantasy, Mystery, Crime, Animation, Documentary, Musical, Western
        - director (TEXT)
        - cast (TEXT)
        - rating (REAL) - values between 5.0 and 9.5
        - plot_summary (TEXT)
        - duration_minutes (INTEGER)
        - language (TEXT)
        - country (TEXT)
        
        Table: movie_viewership
        - id (INTEGER, PRIMARY KEY)
        - movie_id (INTEGER, FOREIGN KEY to movies.id)
        - view_date (DATE)
        - views_count (INTEGER)
        - platform (TEXT) - values: Netflix, Amazon Prime, Disney+, HBO Max, Hulu, Apple TV+, Paramount+, Peacock
        - region (TEXT) - values: North America, Europe, Asia, South America, Australia, Africa, Middle East
        
        Sample Data:
        - We have 100 movies from 1990-2025
        - Each movie has viewership data for the first year after release
        - View counts range from 1,000 to 100,000 per day
        """
        
        self.system_prompt = f"""
        You are a movie database assistant. You can answer questions about movies by querying the database.
        
        {self.schema_info}
        
        When a user asks a question:
        1. Generate the appropriate SQL query
        2. Execute it against the database
        3. Provide a natural, conversational answer based on the results
        
        Examples:
        - "How many movies do you have?" → SELECT COUNT(*) FROM movies → "I have 100 movies in my database!"
        - "Show me action movies from 2024" → SELECT * FROM movies WHERE genre='Action' AND release_date >= '2024-01-01' AND release_date <= '2024-12-31' → "Here are the action movies from 2024: [list movies]"
        - "Find most watched movies of 2025" → SELECT m.*, SUM(mv.views_count) as total_views FROM movies m LEFT JOIN movie_viewership mv ON m.id = mv.movie_id WHERE mv.view_date BETWEEN '2025-01-01' AND '2025-12-31' GROUP BY m.id ORDER BY total_views DESC LIMIT 10 → "The most watched movies of 2025 are: [list with view counts]"
        
        Always provide helpful, natural responses. If no results are found, explain why and suggest alternatives.
        """
    
    def _initialize_llm(self, api_key: str, ai_provider: str):
        """Initialize the appropriate LLM based on the AI provider and API key"""
        if ai_provider == "openai":
            return ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1,
                openai_api_key=api_key
            )
        elif ai_provider == "gemini":
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                temperature=0.1,
                google_api_key=api_key
            )
        else:
            raise ValueError(f"Unsupported AI provider: {ai_provider}")
    
    def execute_sql(self, sql_query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        try:
            db = SessionLocal()
            result = db.execute(text(sql_query))
            
            # Convert result to list of dictionaries
            columns = result.keys()
            rows = result.fetchall()
            
            results = []
            for row in rows:
                row_dict = {}
                for i, column in enumerate(columns):
                    row_dict[column] = row[i]
                results.append(row_dict)
            
            db.close()
            return results
            
        except Exception as e:
            print(f"SQL execution error: {e}")
            return []
    
    def is_conversational(self, query: str) -> bool:
        """Check if query is conversational (greeting, small talk, etc.)"""
        query_lower = query.lower().strip()
        
        # Greeting patterns
        greeting_patterns = [
            r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
            r'\b(how are you|how do you do|what\'s up|sup)\b',
            r'\b(nice to meet you|pleased to meet you)\b'
        ]
        
        # Small talk patterns
        small_talk_patterns = [
            r'\b(what\'s your name|who are you)\b',
            r'\b(what time|what day|what date)\b',
            r'\b(weather|temperature|rain|sunny)\b'
        ]
        
        # Help patterns
        help_patterns = [
            r'\b(help|what can you do|what do you do|how do you work)\b',
            r'\b(commands|options|features)\b'
        ]
        
        import re
        for pattern in greeting_patterns + small_talk_patterns + help_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def get_conversational_response(self, query: str) -> str:
        """Generate conversational response"""
        query_lower = query.lower().strip()
        
        if re.search(r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b', query_lower):
            return "Hello! 👋 I'm your NQL Movie Chatbot. I can help you find and explore movies using natural language! Ask me about any movie, genre, actor, or director."
        
        elif re.search(r'\b(how are you|how do you do|what\'s up)\b', query_lower):
            return "I'm doing great, thank you! 😊 I'm always excited to help you discover amazing movies. How can I assist you today?"
        
        elif re.search(r'\b(what\'s your name|who are you)\b', query_lower):
            return "I'm your NQL Movie Chatbot! 🎬 I specialize in helping you find and explore movies using natural language. I can understand complex queries about films, actors, directors, genres, and more!"
        
        elif re.search(r'\b(help|what can you do|what do you do|how do you work)\b', query_lower):
            return """🎬 **I'm your NQL Movie Chatbot!** Here's what I can help you with:

**🔍 Movie Queries:**
- Find movies by genre, director, or actor
- Search by rating, release date, or popularity
- Get recommendations based on your preferences

**💬 Natural Language:**
Just ask me naturally! For example:
- "Find me the most watched movies this year"
- "Show me the best action movies"
- "What are Christopher Nolan's highest rated films?"

**🎯 Example Questions:**
- "How many movies do you have?"
- "Show me action movies from 2024"
- "Find most watched movies of 2025"

What would you like to explore? 🚀"""
        
        else:
            return "That's interesting! 😊 I'm here to help you with all things movies. What would you like to know about films?"
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process user query directly with LLM"""
        try:
            # Check if it's a conversational message
            if self.is_conversational(query):
                return {
                    "sql_query": "",
                    "results": [],
                    "answer": self.get_conversational_response(query),
                    "success": True,
                    "is_conversational": True
                }
            
            # Get API key and provider from session
            from backend.services.session_manager import session_manager
            session_data = session_manager.get_session(self.session_id)
            if not session_data:
                return {
                    "sql_query": "",
                    "results": [],
                    "answer": "Session expired. Please login again.",
                    "success": False
                }
            
            # Initialize LLM with session API key
            llm = self._initialize_llm(session_data["api_key"], session_data["ai_provider"])
            
            # Ask LLM to generate SQL and provide answer
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""
                User question: "{query}"
                
                Please:
                1. Generate the SQL query needed to answer this question
                2. Execute it (I'll handle the execution)
                3. Provide a natural, conversational answer
                
                Format your response as JSON:
                {{
                    "sql_query": "SELECT ...",
                    "answer": "Natural language answer based on the results"
                }}
                """)
            ]
            
            response = llm.invoke(messages)
            
            # Parse LLM response
            try:
                response_data = json.loads(response.content)
                sql_query = response_data.get("sql_query", "")
                expected_answer = response_data.get("answer", "")
            except json.JSONDecodeError:
                # Fallback if LLM doesn't return JSON
                sql_query = ""
                expected_answer = "I couldn't parse the response properly."
            
            # Execute the SQL query
            results = []
            if sql_query:
                results = self.execute_sql(sql_query)
            
            # Generate final answer
            if results:
                # Create a natural response based on results
                if len(results) == 1 and 'COUNT(*)' in str(results[0]):
                    # Count query
                    count = list(results[0].values())[0]
                    final_answer = f"I found {count} movies in my database."
                elif len(results) == 1 and 'total_movies' in str(results[0]):
                    # Count query with alias
                    count = results[0]['total_movies']
                    final_answer = f"I have {count} movies in my database."
                else:
                    # List of movies
                    if len(results) <= 5:
                        movie_list = []
                        for movie in results:
                            title = movie.get('title', 'Unknown')
                            rating = movie.get('rating', 'N/A')
                            genre = movie.get('genre', 'Unknown')
                            if 'total_views' in movie:
                                views = movie['total_views']
                                movie_list.append(f"• {title} ({genre}) - {views:,} views")
                            else:
                                movie_list.append(f"• {title} ({genre}) - Rating: {rating}")
                        final_answer = f"Here are the movies I found:\n" + "\n".join(movie_list)
                    else:
                        final_answer = f"I found {len(results)} movies. Here are the top results:\n"
                        for i, movie in enumerate(results[:5]):
                            title = movie.get('title', 'Unknown')
                            rating = movie.get('rating', 'N/A')
                            genre = movie.get('genre', 'Unknown')
                            if 'total_views' in movie:
                                views = movie['total_views']
                                final_answer += f"{i+1}. {title} ({genre}) - {views:,} views\n"
                            else:
                                final_answer += f"{i+1}. {title} ({genre}) - Rating: {rating}\n"
                        if len(results) > 5:
                            final_answer += f"... and {len(results) - 5} more movies."
            else:
                final_answer = "I couldn't find any movies matching your criteria. Try asking about a different genre, year, or director."
            
            return {
                "sql_query": sql_query,
                "results": results,
                "answer": final_answer,
                "success": True
            }
            
        except Exception as e:
            return {
                "sql_query": "",
                "results": [],
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "success": False
            }


# Global instance
direct_query_processor = DirectQueryProcessor()
