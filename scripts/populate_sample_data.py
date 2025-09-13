#!/usr/bin/env python3
"""
Script to populate the database with sample movie data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random

from backend.utils.database import engine, init_database
from backend.models.movie import Movie, MovieViewership

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_sample_movies():
    """Create sample movie data"""
    
    sample_movies = [
        {
            "title": "The Dark Knight",
            "release_date": datetime(2008, 7, 18),
            "genre": "Action",
            "director": "Christopher Nolan",
            "cast": "Christian Bale, Heath Ledger, Aaron Eckhart, Michael Caine",
            "rating": 9.0,
            "plot_summary": "Batman faces the Joker in this epic superhero film that explores themes of chaos and order.",
            "duration_minutes": 152,
            "language": "English",
            "country": "USA"
        },
        {
            "title": "Inception",
            "release_date": datetime(2010, 7, 16),
            "genre": "Sci-Fi",
            "director": "Christopher Nolan",
            "cast": "Leonardo DiCaprio, Marion Cotillard, Tom Hardy, Joseph Gordon-Levitt",
            "rating": 8.8,
            "plot_summary": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into a CEO's mind.",
            "duration_minutes": 148,
            "language": "English",
            "country": "USA"
        },
        {
            "title": "Interstellar",
            "release_date": datetime(2014, 11, 7),
            "genre": "Sci-Fi",
            "director": "Christopher Nolan",
            "cast": "Matthew McConaughey, Anne Hathaway, Jessica Chastain, Michael Caine",
            "rating": 8.6,
            "plot_summary": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
            "duration_minutes": 169,
            "language": "English",
            "country": "USA"
        },
        {
            "title": "The Matrix",
            "release_date": datetime(1999, 3, 31),
            "genre": "Action",
            "director": "Lana Wachowski, Lilly Wachowski",
            "cast": "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving",
            "rating": 8.7,
            "plot_summary": "A computer hacker learns about the true nature of reality and his role in the war against its controllers.",
            "duration_minutes": 136,
            "language": "English",
            "country": "USA"
        },
        {
            "title": "Pulp Fiction",
            "release_date": datetime(1994, 10, 14),
            "genre": "Crime",
            "director": "Quentin Tarantino",
            "cast": "John Travolta, Uma Thurman, Samuel L. Jackson, Bruce Willis",
            "rating": 8.9,
            "plot_summary": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
            "duration_minutes": 154,
            "language": "English",
            "country": "USA"
        },
        {
            "title": "The Godfather",
            "release_date": datetime(1972, 3, 24),
            "genre": "Crime",
            "director": "Francis Ford Coppola",
            "cast": "Marlon Brando, Al Pacino, James Caan, Robert Duvall",
            "rating": 9.2,
            "plot_summary": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
            "duration_minutes": 175,
            "language": "English",
            "country": "USA"
        },
        {
            "title": "Parasite",
            "release_date": datetime(2019, 5, 30),
            "genre": "Thriller",
            "director": "Bong Joon-ho",
            "cast": "Song Kang-ho, Lee Sun-kyun, Cho Yeo-jeong, Choi Woo-shik",
            "rating": 8.5,
            "plot_summary": "A poor family schemes to become employed by a wealthy family by infiltrating their household and posing as unrelated, highly qualified individuals.",
            "duration_minutes": 132,
            "language": "Korean",
            "country": "South Korea"
        },
        {
            "title": "Spirited Away",
            "release_date": datetime(2001, 7, 20),
            "genre": "Animation",
            "director": "Hayao Miyazaki",
            "cast": "Rumi Hiiragi, Miyu Irino, Mari Natsuki, Takashi Naitô",
            "rating": 8.6,
            "plot_summary": "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by witches and populated by strange creatures.",
            "duration_minutes": 125,
            "language": "Japanese",
            "country": "Japan"
        }
    ]
    
    return sample_movies

def create_sample_viewership(movie_id: int, start_date: datetime, end_date: datetime):
    """Create sample viewership data for a movie"""
    viewership_data = []
    current_date = start_date
    
    while current_date <= end_date:
        # Random view count between 1000 and 50000
        views = random.randint(1000, 50000)
        
        # Random platform
        platforms = ["Netflix", "Amazon Prime", "Disney+", "HBO Max", "Hulu"]
        platform = random.choice(platforms)
        
        # Random region
        regions = ["North America", "Europe", "Asia", "South America", "Australia"]
        region = random.choice(regions)
        
        viewership_data.append({
            "movie_id": movie_id,
            "view_date": current_date,
            "views_count": views,
            "platform": platform,
            "region": region
        })
        
        current_date += timedelta(days=1)
    
    return viewership_data

def populate_database():
    """Populate the database with sample data"""
    print("Initializing database...")
    init_database()
    
    print("Creating sample movies...")
    db = SessionLocal()
    
    try:
        # Create movies
        sample_movies = create_sample_movies()
        created_movies = []
        
        for movie_data in sample_movies:
            movie = Movie(**movie_data)
            db.add(movie)
            db.flush()  # Get the ID
            created_movies.append(movie)
        
        db.commit()
        print(f"Created {len(created_movies)} movies")
        
        # Create viewership data for the last 30 days
        print("Creating sample viewership data...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        for movie in created_movies:
            viewership_data = create_sample_viewership(
                movie.id, 
                start_date, 
                end_date
            )
            
            for view_data in viewership_data:
                viewership = MovieViewership(**view_data)
                db.add(viewership)
        
        db.commit()
        print("Created viewership data for the last 30 days")
        
        print("Database populated successfully!")
        
    except Exception as e:
        print(f"Error populating database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_database()
