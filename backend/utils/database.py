from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/movies.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    from backend.models.movie import Base
    Base.metadata.create_all(bind=engine)


def init_database():
    """Initialize database with tables"""
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Check if we should skip table creation (for existing production databases)
    skip_creation = os.getenv("SKIP_TABLE_CREATION", "false").lower() == "true"
    use_production_db = os.getenv("USE_PRODUCTION_DB", "false").lower() == "true"
    
    if skip_creation or use_production_db:
        print("✅ Using existing database schema (skipping table creation)")
        print("📊 MCP will adapt to your existing schema automatically")
        return
    
    # For new/development databases, check if tables already exist
    from sqlalchemy import inspect
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if existing_tables:
        # Tables already exist, don't recreate
        print(f"✅ Found existing tables: {', '.join(existing_tables)}")
        print("📊 Using existing schema, MCP will adapt automatically")
    else:
        # No tables found, create them from our models
        create_tables()
        print("✅ Database tables created successfully from models!")
