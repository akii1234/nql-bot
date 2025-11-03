"""
MCP Query Router - Uses Model Context Protocol for better database access
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time

from backend.services.mcp_query_processor import MCPQueryProcessor

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
    answer: Optional[str] = None
    error_message: Optional[str] = None
    is_conversational: Optional[bool] = False


@router.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a natural language query using MCP approach"""
    start_time = time.time()
    
    try:
        # Initialize MCP processor with session
        processor = MCPQueryProcessor(request.session_id)
        
        # Process query
        result = processor.process_query(request.query)
        
        execution_time = int((time.time() - start_time) * 1000)
        
        if result["success"]:
            response_type = "conversation" if result.get("is_conversational", False) else "movie_query"
            
            return QueryResponse(
                query=request.query,
                response_type=response_type,
                results=result["results"],
                execution_time_ms=execution_time,
                sql_query=result["sql_query"],
                answer=result["answer"],
                is_conversational=result.get("is_conversational", False)
            )
        else:
            return QueryResponse(
                query=request.query,
                response_type="error",
                execution_time_ms=execution_time,
                error_message=result["answer"]
            )
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        return QueryResponse(
            query=request.query,
            response_type="error",
            execution_time_ms=execution_time,
            error_message=f"Error: {str(e)}"
        )


@router.get("/")
async def get_info():
    """Get information about the MCP query API"""
    return {
        "message": "MCP Query API - Model Context Protocol approach",
        "description": "Uses MCP to give LLM direct, structured access to your database",
        "features": [
            "Dynamic schema detection",
            "Real-time database context",
            "Improved query accuracy",
            "Better error handling"
        ],
        "endpoints": {
            "POST /api/queries/process": "Process natural language queries using MCP"
        }
    }
