from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from backend.utils.database import init_database
from backend.routers import queries, setup

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting NQL Movie Chatbot...")
    init_database()
    print("Database initialized!")
    yield
    # Shutdown
    print("Shutting down NQL Movie Chatbot...")


# Create FastAPI app
app = FastAPI(
    title="NQL Movie Chatbot",
    description="Natural Query Language chatbot for movie queries using LangChain",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(queries.router)
app.include_router(setup.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to NQL Movie Chatbot!",
        "version": "0.1.0",
        "endpoints": {
            "docs": "/docs",
            "setup": "/api/setup/user-setup",
            "process_query": "/api/queries/process",
            "sample_movies": "/api/queries/sample"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "NQL Movie Chatbot"}


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
