from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
import time

from backend.utils.database import get_db
from backend.services.session_query_processor import SessionQueryProcessor
from backend.services.query_processor import QueryIntent
from backend.services.session_manager import session_manager
from backend.services.conversation_handler import conversation_handler
from backend.models.movie import Movie, MovieViewership

router = APIRouter(prefix="/api/queries", tags=["queries"])


class QueryRequest(BaseModel):
    query: str
    session_id: str


class QueryResponse(BaseModel):
    query: str
    response_type: str  # "conversation" or "movie_query"
    conversation_response: Dict[str, Any] = None
    parsed_intent: Dict[str, Any] = None
    results: List[Dict[str, Any]] = None
    execution_time_ms: int = None
    sql_query: str = None


class MovieResult(BaseModel):
    id: int
    title: str
    release_date: str = None
    genre: str = None
    director: str = None
    cast: str = None
    rating: float = None
    plot_summary: str = None
    duration_minutes: int = None
    language: str = None
    country: str = None
    total_views: int = None


@router.post("/process", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Process a natural language query about movies"""
    start_time = time.time()
    
    try:
        # Validate session
        session_data = session_manager.get_session(request.session_id)
        if not session_data:
            raise HTTPException(status_code=401, detail="Invalid or expired session. Please login again.")
        
        # Check if this is a conversational message
        conversation_response = conversation_handler.process_message(
            request.query, 
            session_data["user_name"]
        )
        
        # If it's a conversation response, return it directly
        if conversation_response["type"] != "movie_query":
            return QueryResponse(
                query=request.query,
                response_type="conversation",
                conversation_response=conversation_response
            )
        
        # Otherwise, process as a movie query
        processor = SessionQueryProcessor(request.session_id)
        
        # Parse the natural language query
        intent = processor.parse_query(request.query)
        
        # Generate SQL query
        sql_query = processor.generate_sql_query(intent)
        
        # Execute query (simplified - in production you'd use proper SQL execution)
        results = await execute_movie_query(db, sql_query, intent)
        
        execution_time = int((time.time() - start_time) * 1000)
        
        return QueryResponse(
            query=request.query,
            response_type="movie_query",
            parsed_intent=intent.dict(),
            results=results,
            execution_time_ms=execution_time,
            sql_query=sql_query
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


async def execute_movie_query(db: Session, sql_query: str, intent: QueryIntent) -> List[Dict[str, Any]]:
    """Execute the generated SQL query and return results"""
    try:
        # Execute the actual SQL query
        from sqlalchemy import text
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
        
        return results
            
    except Exception as e:
        print(f"Error executing query: {e}")
        return []


@router.get("/sample", response_model=List[MovieResult])
async def get_sample_movies(db: Session = Depends(get_db)):
    """Get sample movies for testing"""
    # Return sample data for now
    sample_movies = [
        MovieResult(
            id=1,
            title="The Dark Knight",
            release_date="2008-07-18",
            genre="Action",
            director="Christopher Nolan",
            cast="Christian Bale, Heath Ledger, Aaron Eckhart",
            rating=9.0,
            plot_summary="Batman faces the Joker in this epic superhero film",
            duration_minutes=152,
            language="English",
            country="USA",
            total_views=1500000
        ),
        MovieResult(
            id=2,
            title="Inception",
            release_date="2010-07-16",
            genre="Sci-Fi",
            director="Christopher Nolan",
            cast="Leonardo DiCaprio, Marion Cotillard, Tom Hardy",
            rating=8.8,
            plot_summary="A thief who steals corporate secrets through dream-sharing technology",
            duration_minutes=148,
            language="English",
            country="USA",
            total_views=1200000
        )
    ]
    
    return sample_movies
