"""
Direct Query Router - New simplified approach using direct LLM processing
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time

from backend.services.direct_query_processor import direct_query_processor

router = APIRouter(prefix="/api/queries", tags=["queries"])


class QueryRequest(BaseModel):
    query: str
    session_id: str


class QueryResponse(BaseModel):
    query: str
    response_type: str  # "movie_query", "conversation", or "error"
    results: Optional[List[Dict[str, Any]]] = None
    execution_time_ms: int
    sql_query: Optional[str] = None
    answer: Optional[str] = None  # Natural language answer
    error_message: Optional[str] = None
    is_conversational: Optional[bool] = False


@router.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a natural language query about movies using direct LLM approach"""
    start_time = time.time()
    
    try:
        # Use the new direct query processor with session
        processor = DirectQueryProcessor(request.session_id)
        result = processor.process_query(request.query)
        
        execution_time = int((time.time() - start_time) * 1000)
        
        if result["success"]:
            # Determine response type
            response_type = "conversation" if result.get("is_conversational", False) else "movie_query"
            
            return QueryResponse(
                query=request.query,
                response_type=response_type,
                results=result["results"],
                execution_time_ms=execution_time,
                sql_query=result["sql_query"],
                answer=result["answer"],  # Natural language answer
                is_conversational=result.get("is_conversational", False)
            )
        else:
            return QueryResponse(
                query=request.query,
                response_type="error",
                error_message=result["answer"],
                execution_time_ms=execution_time
            )
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        return QueryResponse(
            query=request.query,
            response_type="error",
            error_message=f"Sorry, I encountered an error: {str(e)}",
            execution_time_ms=execution_time
        )


@router.get("/")
async def get_queries_info():
    """Get information about available query endpoints"""
    return {
        "message": "Direct Query API - Simple LLM approach",
        "endpoints": {
            "POST /api/queries/process": "Process natural language movie queries"
        },
        "examples": [
            "How many movies do you have?",
            "Show me action movies from 2024",
            "Find most watched movies of 2025",
            "What are the highest rated drama movies?",
            "Show me movies by Christopher Nolan"
        ]
    }
