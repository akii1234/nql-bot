"""
OLD QUERY PROCESSOR - COMMENTED OUT FOR REFERENCE
This was the complex approach that required constant fixes.
We've switched to DirectQueryProcessor for better reliability.
"""

# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import os
from dotenv import load_dotenv

load_dotenv()


class QueryIntent(BaseModel):
    """Structured representation of user query intent"""
    intent_type: str  # "search", "filter", "aggregate", "compare", "direct_sql"
    entities: List[str]  # Movie titles, genres, actors, etc.
    filters: Dict[str, Any]  # Date ranges, ratings, etc.
    aggregation: Optional[str]  # "most_watched", "highest_rated", etc.
    time_range: Optional[Dict[str, Optional[str]]]  # {"start": "2025-01-01", "end": "2025-02-03"} or {"start": "2025-01-01", "end": None}
    sql_query: Optional[str] = None  # LLM-generated SQL query


class NQLQueryProcessor:
    """Natural Query Language processor for movie queries"""
    
    def __init__(self):
        self.ai_provider = os.getenv("AI_PROVIDER", "gemini").lower()
        self.llm = self._initialize_llm()
        
        self.system_prompt = """
        You are a Natural Query Language (NQL) processor for a movie database system.
        Your job is to parse natural language queries about movies and convert them into structured data.

        Available movie attributes:
        - title, release_date, genre, director, cast, rating, plot_summary, duration_minutes, language, country
        - viewership data: view_date, views_count, platform, region

        Common query patterns:
        1. "Find movies most watched between [date1] and [date2]" -> intent: aggregate, aggregation: most_watched, time_range: {start, end}
        2. "Find movies most watched after [date]" -> intent: aggregate, aggregation: most_watched, time_range: {start: "date", end: null}
        3. "Find movies most watched before [date]" -> intent: aggregate, aggregation: most_watched, time_range: {start: null, end: "date"}
        4. "Show me action movies from 2024" -> intent: filter, filters: {genre: "action", release_date: "2024"}
        5. "What are the highest rated movies?" -> intent: aggregate, aggregation: highest_rated
        6. "Find movies by Christopher Nolan" -> intent: filter, filters: {director: "Christopher Nolan"}
        7. "How many movies do you have?" -> intent: count, aggregation: count_total
        8. "Show me the total number of movies" -> intent: count, aggregation: count_total
        9. "Count all movies" -> intent: count, aggregation: count_total
        10. "Find most watched movies in drama category in 2025" -> intent: aggregate, aggregation: most_watched, filters: {genre: "drama"}, time_range: {start: "2025-01-01", end: "2025-12-31"}
        11. "Show me comedy films from 2024" -> intent: filter, filters: {genre: "comedy", release_date: "2024"}
        12. "What are the best horror movies?" -> intent: aggregate, aggregation: highest_rated, filters: {genre: "horror"}

        Always respond with valid JSON in this exact format:
        {
            "intent_type": "search|filter|aggregate|compare|count",
            "entities": ["list", "of", "extracted", "entities"],
            "filters": {
                "genre": "action",
                "director": "Christopher Nolan",
                "rating_min": 8.0,
                "release_year": 2024
            },
            "aggregation": "most_watched|highest_rated|most_recent|longest|shortest|count_total",
            "time_range": {
                "start": "2025-01-01",
                "end": "2025-02-03"
            }
        }
        """
    
    def _initialize_llm(self):
        """Initialize the appropriate LLM based on the AI provider"""
        if self.ai_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            return ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1,
                api_key=api_key
            )
        elif self.ai_provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                temperature=0.1,
                google_api_key=api_key
            )
        else:
            raise ValueError(f"Unsupported AI provider: {self.ai_provider}")
    
    def parse_query(self, query: str) -> QueryIntent:
        """Parse natural language query into structured intent"""
        try:
            # SIMPLE APPROACH: Let LLM generate SQL directly instead of parsing
            messages = [
                SystemMessage(content=f"""
                You are a movie database assistant. Generate SQL queries for movie questions.
                
                Database schema:
                - movies table: id, title, release_date, genre, director, cast, rating, plot_summary, duration_minutes, language, country
                - movie_viewership table: id, movie_id, view_date, views_count, platform, region
                
                Examples:
                - "How many movies do you have?" → SELECT COUNT(*) FROM movies
                - "Show me action movies from 2024" → SELECT * FROM movies WHERE genre='Action' AND release_date >= '2024-01-01' AND release_date <= '2024-12-31'
                - "Find most watched movies of 2025" → SELECT m.*, SUM(mv.views_count) as total_views FROM movies m LEFT JOIN movie_viewership mv ON m.id = mv.movie_id WHERE mv.view_date BETWEEN '2025-01-01' AND '2025-12-31' GROUP BY m.id ORDER BY total_views DESC LIMIT 10
                
                Just return the SQL query, nothing else.
                """),
                HumanMessage(content=f"Generate SQL for: {query}")
            ]
            
            response = self.llm.invoke(messages)
            sql_query = response.content.strip()
            
            # Return a simple intent that will use the LLM-generated SQL
            return QueryIntent(
                intent_type="direct_sql",
                entities=[],
                filters={},
                aggregation=None,
                time_range=None,
                sql_query=sql_query  # Store the LLM-generated SQL
            )
            
        except Exception as e:
            print(f"Error generating SQL: {e}")
            # Fallback to basic parsing
            return self._fallback_parse(query)
    
    def _fallback_parse(self, query: str) -> QueryIntent:
        """Fallback parsing for when LLM fails"""
        query_lower = query.lower()
        
        # Basic intent detection
        if any(word in query_lower for word in ["how many", "count", "total number", "number of"]):
            intent_type = "count"
            aggregation = "count_total"
        elif any(word in query_lower for word in ["most watched", "popular", "trending"]):
            intent_type = "aggregate"
            aggregation = "most_watched"
        elif any(word in query_lower for word in ["highest rated", "best rated", "top rated"]):
            intent_type = "aggregate"
            aggregation = "highest_rated"
        elif any(word in query_lower for word in ["find", "show", "get", "list"]):
            intent_type = "filter"
            aggregation = None
        else:
            intent_type = "search"
            aggregation = None
        
        # Extract filters (genre, director, etc.)
        filters = {}
        
        # Genre detection
        genres = ["action", "comedy", "drama", "horror", "sci-fi", "romance", "thriller", "adventure", "fantasy", "mystery", "crime", "animation", "documentary", "musical", "western"]
        for genre in genres:
            if genre in query_lower or f"{genre} category" in query_lower or f"{genre} movies" in query_lower or f"{genre} films" in query_lower:
                filters["genre"] = genre.title()
                break
        
        # Director detection
        if "by " in query_lower:
            # Simple director extraction - look for "by [name]"
            import re
            director_match = re.search(r'by\s+([A-Za-z\s]+?)(?:\s|$)', query_lower)
            if director_match:
                director_name = director_match.group(1).strip().title()
                filters["director"] = director_name
        
        # Extract time range (improved date detection)
        time_range = None
        
        # Look for date patterns
        import re
        
        # Month mapping
        month_map = {
            'jan': '01', 'january': '01',
            'feb': '02', 'february': '02',
            'mar': '03', 'march': '03',
            'apr': '04', 'april': '04',
            'may': '05',
            'jun': '06', 'june': '06',
            'jul': '07', 'july': '07',
            'aug': '08', 'august': '08',
            'sep': '09', 'september': '09',
            'oct': '10', 'october': '10',
            'nov': '11', 'november': '11',
            'dec': '12', 'december': '12'
        }
        
        # Pattern for "after [date]" or "from [date]" - more flexible
        after_pattern = r'(?:after|from|since)\s+(?:1st\s+)?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)\s+(\d{4})'
        after_match = re.search(after_pattern, query_lower)
        
        # Pattern for "before [date]" or "until [date]"
        before_pattern = r'(?:before|until|till)\s+(?:1st\s+)?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)\s+(\d{4})'
        before_match = re.search(before_pattern, query_lower)
        
        # Pattern for "between [date] and [date]"
        between_pattern = r'between\s+(?:1st\s+)?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)\s+(\d{4})\s+and\s+(?:3rd\s+)?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)\s+(\d{4})'
        between_match = re.search(between_pattern, query_lower)
        
        if between_match:
            month1, year1, month2, year2 = between_match.groups()
            month1_num = month_map.get(month1.lower(), '01')
            month2_num = month_map.get(month2.lower(), '02')
            time_range = {"start": f"{year1}-{month1_num}-01", "end": f"{year2}-{month2_num}-03"}
        elif after_match:
            month, year = after_match.groups()
            month_num = month_map.get(month.lower(), '01')
            time_range = {"start": f"{year}-{month_num}-01", "end": None}
        elif before_match:
            month, year = before_match.groups()
            month_num = month_map.get(month.lower(), '01')
            time_range = {"start": None, "end": f"{year}-{month_num}-01"}
        elif "2025" in query_lower and ("after" in query_lower or "from" in query_lower):
            # Fallback for simple "after 2025" without month
            time_range = {"start": "2025-01-01", "end": None}
        elif re.search(r'\b(?:of|in|from|during)\s+(\d{4})\b', query_lower):
            # Pattern for "of 2025", "in 2025", "from 2025", "during 2025"
            year_match = re.search(r'\b(?:of|in|from|during)\s+(\d{4})\b', query_lower)
            if year_match:
                year = year_match.group(1)
                time_range = {"start": f"{year}-01-01", "end": f"{year}-12-31"}
        
        return QueryIntent(
            intent_type=intent_type,
            entities=[],
            filters=filters,
            aggregation=aggregation,
            time_range=time_range
        )
    
    def generate_sql_query(self, intent: QueryIntent) -> str:
        """Generate SQL query from parsed intent"""
        
        # SIMPLE APPROACH: Use LLM-generated SQL directly
        if hasattr(intent, 'sql_query') and intent.sql_query:
            return intent.sql_query
        
        # Handle count queries
        if intent.intent_type == "count" and intent.aggregation == "count_total":
            base_query = "SELECT COUNT(*) as total_movies FROM movies m"
            
            # Add filters if specified
            if intent.filters:
                where_clauses = []
                for key, value in intent.filters.items():
                    if key == "genre":
                        where_clauses.append(f"m.genre = '{value}'")
                    elif key == "director":
                        where_clauses.append(f"m.director LIKE '%{value}%'")
                    elif key == "rating_min":
                        where_clauses.append(f"m.rating >= {value}")
                
                if where_clauses:
                    base_query += " WHERE " + " AND ".join(where_clauses)
            
            return base_query
        
        # Handle other query types
        base_query = "SELECT m.*, SUM(mv.views_count) as total_views FROM movies m"
        
        if intent.aggregation == "most_watched":
            base_query += " LEFT JOIN movie_viewership mv ON m.id = mv.movie_id"
            
            # Add time filter if specified
            if intent.time_range:
                if intent.time_range['start'] and intent.time_range['end']:
                    # Between dates
                    base_query += f" WHERE mv.view_date BETWEEN '{intent.time_range['start']}' AND '{intent.time_range['end']}'"
                elif intent.time_range['start']:
                    # After date
                    base_query += f" WHERE mv.view_date >= '{intent.time_range['start']}'"
                elif intent.time_range['end']:
                    # Before date
                    base_query += f" WHERE mv.view_date <= '{intent.time_range['end']}'"
            
            # Add other filters
            if intent.filters:
                for key, value in intent.filters.items():
                    if key == "genre":
                        if "WHERE" in base_query:
                            base_query += f" AND m.genre = '{value}'"
                        else:
                            base_query += f" WHERE m.genre = '{value}'"
                    elif key == "director":
                        if "WHERE" in base_query:
                            base_query += f" AND m.director LIKE '%{value}%'"
                        else:
                            base_query += f" WHERE m.director LIKE '%{value}%'"
                    elif key == "rating_min":
                        if "WHERE" in base_query:
                            base_query += f" AND m.rating >= {value}"
                        else:
                            base_query += f" WHERE m.rating >= {value}"
            
            base_query += " GROUP BY m.id ORDER BY total_views DESC LIMIT 10"
            
        elif intent.aggregation == "highest_rated":
            base_query += " WHERE m.rating IS NOT NULL"
            
            if intent.filters:
                for key, value in intent.filters.items():
                    if key == "genre":
                        base_query += f" AND m.genre = '{value}'"
                    elif key == "director":
                        base_query += f" AND m.director LIKE '%{value}%'"
            
            base_query += " ORDER BY m.rating DESC LIMIT 10"
            
        else:
            # Basic filter query
            if intent.filters:
                conditions = []
                for key, value in intent.filters.items():
                    if key == "genre":
                        conditions.append(f"m.genre = '{value}'")
                    elif key == "director":
                        conditions.append(f"m.director LIKE '%{value}%'")
                    elif key == "title":
                        conditions.append(f"m.title LIKE '%{value}%'")
                
                if conditions:
                    base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += " LIMIT 20"
        
        return base_query
