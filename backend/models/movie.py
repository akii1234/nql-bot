from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    release_date = Column(DateTime, nullable=True)
    genre = Column(String(100), nullable=True)
    director = Column(String(255), nullable=True)
    cast = Column(Text, nullable=True)  # JSON string of cast members
    rating = Column(Float, nullable=True)
    plot_summary = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    language = Column(String(50), nullable=True)
    country = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with viewership data
    viewership = relationship("MovieViewership", back_populates="movie")


class MovieViewership(Base):
    __tablename__ = "movie_viewership"
    
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    view_date = Column(DateTime, nullable=False, index=True)
    views_count = Column(Integer, nullable=False, default=0)
    platform = Column(String(100), nullable=True)  # Netflix, Amazon Prime, etc.
    region = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with movie
    movie = relationship("Movie", back_populates="viewership")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with queries
    queries = relationship("UserQuery", back_populates="user")


class UserQuery(Base):
    __tablename__ = "user_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query_text = Column(Text, nullable=False)
    parsed_query = Column(Text, nullable=True)  # JSON string of parsed query
    response = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with user
    user = relationship("User", back_populates="queries")
