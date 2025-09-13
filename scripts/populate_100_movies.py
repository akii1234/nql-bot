#!/usr/bin/env python3
"""
Script to populate the database with 100 random movies with different years
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

def generate_random_movies(count=100):
    """Generate random movie data"""
    
    # Movie data pools
    titles = [
        "The Last Guardian", "Eternal Dreams", "Midnight Express", "Golden Horizon", "Silver Bullet",
        "Dark Phoenix", "Crimson Tide", "Blue Moon", "Green Lantern", "Purple Rain",
        "The Final Countdown", "Endless Summer", "Winter's Tale", "Spring Awakening", "Autumn Leaves",
        "City of Angels", "Town of Dreams", "Village of Hope", "Island of Lost Souls", "Mountain of Fire",
        "Ocean's Eleven", "River's Edge", "Desert Storm", "Forest Gump", "Jungle Book",
        "Space Odyssey", "Time Machine", "Dimension X", "Parallel Universe", "Quantum Leap",
        "The Secret Garden", "Hidden Treasure", "Lost World", "Forgotten Kingdom", "Ancient Prophecy",
        "Future Shock", "Past Lives", "Present Moment", "Eternal Now", "Infinite Loop",
        "The Great Escape", "Big Adventure", "Small World", "Tall Tale", "Short Story",
        "Love Story", "War Story", "Peace Story", "Hope Story", "Dream Story",
        "The Chosen One", "The Last Stand", "The First Contact", "The Final Battle", "The New Beginning",
        "Rising Sun", "Setting Moon", "Morning Star", "Evening Star", "Midnight Sun",
        "The Guardian", "The Protector", "The Defender", "The Warrior", "The Hero",
        "Shadow of the Past", "Light of the Future", "Echo of the Present", "Voice of the People", "Heart of the Matter",
        "The Journey Begins", "The Quest Continues", "The Adventure Ends", "The Story Unfolds", "The Legend Lives",
        "Beyond the Horizon", "Above the Clouds", "Below the Surface", "Inside the Mind", "Outside the Box",
        "The Perfect Storm", "The Calm Before", "The Eye of the Storm", "The Aftermath", "The Rebuilding",
        "Digital Dreams", "Analog Reality", "Virtual World", "Real Life", "Mixed Reality",
        "The Last Dance", "The First Step", "The Middle Ground", "The End Game", "The New Deal",
        "Breaking Point", "Turning Point", "Starting Point", "Ending Point", "Meeting Point",
        "The Final Frontier", "The Unknown Territory", "The Familiar Ground", "The Safe Haven", "The Danger Zone"
    ]
    
    genres = ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance", "Thriller", "Adventure", "Fantasy", "Mystery", "Crime", "Animation", "Documentary", "Musical", "Western"]
    
    directors = [
        "Christopher Nolan", "Steven Spielberg", "Martin Scorsese", "Quentin Tarantino", "Ridley Scott",
        "James Cameron", "Peter Jackson", "Tim Burton", "Wes Anderson", "David Fincher",
        "Alfred Hitchcock", "Stanley Kubrick", "Francis Ford Coppola", "George Lucas", "Clint Eastwood",
        "Woody Allen", "Spike Lee", "Coen Brothers", "Darren Aronofsky", "Paul Thomas Anderson",
        "Denis Villeneuve", "Jordan Peele", "Greta Gerwig", "Ava DuVernay", "Ryan Coogler",
        "Taika Waititi", "Bong Joon-ho", "Park Chan-wook", "Hayao Miyazaki", "Akira Kurosawa"
    ]
    
    actors = [
        "Leonardo DiCaprio", "Tom Hanks", "Meryl Streep", "Denzel Washington", "Cate Blanchett",
        "Brad Pitt", "Angelina Jolie", "Will Smith", "Emma Stone", "Ryan Gosling",
        "Jennifer Lawrence", "Chris Evans", "Scarlett Johansson", "Robert Downey Jr.", "Chris Hemsworth",
        "Margot Robbie", "Timothée Chalamet", "Zendaya", "Tom Holland", "Florence Pugh",
        "Michael B. Jordan", "Lupita Nyong'o", "Chadwick Boseman", "Viola Davis", "Mahershala Ali",
        "Sandra Bullock", "George Clooney", "Julia Roberts", "Matt Damon", "Ben Affleck"
    ]
    
    languages = ["English", "Spanish", "French", "German", "Italian", "Japanese", "Korean", "Chinese", "Hindi", "Portuguese"]
    countries = ["USA", "UK", "France", "Germany", "Italy", "Japan", "South Korea", "China", "India", "Brazil", "Canada", "Australia", "Spain", "Mexico", "Russia"]
    
    movies = []
    
    for i in range(count):
        # Random year between 1990 and 2025
        year = random.randint(1990, 2025)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Safe day for all months
        
        # Random title (avoid duplicates)
        title = random.choice(titles)
        if any(movie['title'] == title for movie in movies):
            title = f"{title} {random.randint(1, 999)}"
        
        # Random genre
        genre = random.choice(genres)
        
        # Random director
        director = random.choice(directors)
        
        # Random cast (2-4 actors)
        cast_count = random.randint(2, 4)
        cast = ", ".join(random.sample(actors, cast_count))
        
        # Random rating (5.0 to 9.5)
        rating = round(random.uniform(5.0, 9.5), 1)
        
        # Random duration (90 to 180 minutes)
        duration = random.randint(90, 180)
        
        # Random language and country
        language = random.choice(languages)
        country = random.choice(countries)
        
        # Generate plot summary
        plot_summary = f"A {genre.lower()} film about {random.choice(['adventure', 'mystery', 'romance', 'conflict', 'discovery', 'journey', 'transformation'])} that takes place in {random.choice(['a distant future', 'the past', 'an alternate reality', 'a small town', 'a big city', 'outer space', 'the ocean depths'])}."
        
        movie = {
            "title": title,
            "release_date": datetime(year, month, day),
            "genre": genre,
            "director": director,
            "cast": cast,
            "rating": rating,
            "plot_summary": plot_summary,
            "duration_minutes": duration,
            "language": language,
            "country": country
        }
        
        movies.append(movie)
    
    return movies

def create_viewership_data(movie_id: int, release_date: datetime):
    """Create viewership data for a movie"""
    viewership_data = []
    
    # Create viewership data for the first year after release
    start_date = release_date
    end_date = release_date + timedelta(days=365)
    
    # Create data for every 7 days (weekly data)
    current_date = start_date
    while current_date <= end_date:
        # Random view count (higher for recent movies)
        days_since_release = (current_date - release_date).days
        if days_since_release < 30:
            # First month: high views
            views = random.randint(10000, 100000)
        elif days_since_release < 90:
            # First 3 months: medium views
            views = random.randint(5000, 50000)
        else:
            # Later: lower views
            views = random.randint(1000, 20000)
        
        # Random platform
        platforms = ["Netflix", "Amazon Prime", "Disney+", "HBO Max", "Hulu", "Apple TV+", "Paramount+", "Peacock"]
        platform = random.choice(platforms)
        
        # Random region
        regions = ["North America", "Europe", "Asia", "South America", "Australia", "Africa", "Middle East"]
        region = random.choice(regions)
        
        viewership_data.append({
            "movie_id": movie_id,
            "view_date": current_date,
            "views_count": views,
            "platform": platform,
            "region": region
        })
        
        current_date += timedelta(days=7)
    
    return viewership_data

def populate_database():
    """Populate the database with 100 random movies"""
    print("Initializing database...")
    init_database()
    
    print("Generating 100 random movies...")
    db = SessionLocal()
    
    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(MovieViewership).delete()
        db.query(Movie).delete()
        db.commit()
        
        # Generate and create movies
        random_movies = generate_random_movies(100)
        created_movies = []
        
        print("Creating movies...")
        for i, movie_data in enumerate(random_movies, 1):
            movie = Movie(**movie_data)
            db.add(movie)
            db.flush()  # Get the ID
            created_movies.append(movie)
            
            if i % 10 == 0:
                print(f"Created {i}/100 movies...")
        
        db.commit()
        print(f"✅ Created {len(created_movies)} movies")
        
        # Create viewership data
        print("Creating viewership data...")
        for i, movie in enumerate(created_movies, 1):
            viewership_data = create_viewership_data(movie.id, movie.release_date)
            
            for view_data in viewership_data:
                viewership = MovieViewership(**view_data)
                db.add(viewership)
            
            if i % 10 == 0:
                print(f"Created viewership data for {i}/100 movies...")
        
        db.commit()
        print("✅ Created viewership data for all movies")
        
        # Show summary
        print("\n📊 Database Summary:")
        print(f"Total movies: {len(created_movies)}")
        
        # Show year distribution
        year_counts = {}
        for movie in created_movies:
            year = movie.release_date.year
            year_counts[year] = year_counts.get(year, 0) + 1
        
        print("\n📅 Movies by year:")
        for year in sorted(year_counts.keys()):
            print(f"  {year}: {year_counts[year]} movies")
        
        # Show genre distribution
        genre_counts = {}
        for movie in created_movies:
            genre = movie.genre
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        print("\n🎬 Movies by genre:")
        for genre in sorted(genre_counts.keys()):
            print(f"  {genre}: {genre_counts[genre]} movies")
        
        print("\n🎉 Database populated successfully with 100 random movies!")
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_database()
