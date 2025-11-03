# Database Integration Guide 🗄️

This guide explains how to integrate NQL Bot with your own movie database.

## Quick Start (Sample Data)

If you just want to test the application with sample data:

```bash
# 1. Clone the repository
git clone https://github.com/akhiltripathi/nql-bot.git
cd nql-bot

# 2. Install dependencies
uv sync

# 3. Populate sample database with 100 movies
uv run python scripts/populate_100_movies.py

# 4. Start the application
./start.sh

# 5. Open http://localhost:8501 in your browser
# 6. Enter your name, choose AI provider (OpenAI or Gemini)
# 7. Enter your API key
# 8. Start chatting about movies!
```

## Integration with Your Own Database

### Step 1: Check Your Database Schema

Your database should ideally have:
- A **movies table** with fields like: title, genre, director, rating, release_date, etc.
- (Optional) A **viewership/analytics table** for watch statistics

### Step 2: Analyze Your Database

```bash
# 1. Copy environment template
cp env.example .env

# 2. Edit .env and set your database URL
nano .env

# For PostgreSQL:
DATABASE_URL=postgresql://username:password@localhost:5432/your_database

# For MySQL:
DATABASE_URL=mysql://username:password@localhost:3306/your_database

# For SQLite:
DATABASE_URL=sqlite:///path/to/your/database.db

# 3. Run the database analyzer
uv run python production/scripts/analyze_database.py
```

**The analyzer will show you:**
- ✅ All tables in your database
- ✅ All columns with their data types
- ✅ Whether your schema matches our expected format
- ✅ What field mappings you need to configure
- ✅ Test queries to verify everything works

### Step 3: Update LLM Prompt with Your Schema

The most important step! Edit `backend/services/query_processor.py`:

Find this section (around line 106-115):
```python
Database schema:
- movies table: id, title, release_date, genre, director, cast, rating, plot_summary, duration_minutes, language, country
- movie_viewership table: id, movie_id, view_date, views_count, platform, region
```

**Replace with YOUR actual schema:**
```python
Database schema:
- films table: film_id, film_title, release_year, film_genre, director_name, actors, imdb_rating, description, runtime, lang, country
- analytics table: id, film_id, watch_date, watch_count, streaming_platform, region
```

### Step 4: Update LLM Examples (Optional)

In the same file, update the SQL examples to match your table/column names:

**Before:**
```python
- "How many movies do you have?" → SELECT COUNT(*) FROM movies
```

**After (with your schema):**
```python
- "How many movies do you have?" → SELECT COUNT(*) FROM films
- "Show me action movies from 2024" → SELECT * FROM films WHERE film_genre='Action' AND release_year='2024'
```

### Step 5: Test with Sample Queries

```bash
# Start the application
./start.sh

# Open http://localhost:8501
# Enter your API key
# Test queries like:
# - "How many movies are in the database?"
# - "Show me all movies from 2024"
# - "Find the highest rated movies"
```

## Advanced Configuration

### If Your Schema is Significantly Different

1. **Update field mappings** in `production/config/schema_mappings.json`:

```json
{
  "your_custom_schema": {
    "description": "Your custom database schema",
    "mappings": {
      "movie_id": "your_id_field",
      "title": "your_title_field",
      "genre": "your_genre_field",
      "director": "your_director_field",
      "rating": "your_rating_field"
    }
  }
}
```

2. **Use the production adapter** - See `production/README.md` for details.

## Common Integration Patterns

### Pattern 1: PostgreSQL with Standard Schema
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/movies_db
# No schema changes needed
```

### Pattern 2: MySQL with Different Column Names
```bash
DATABASE_URL=mysql://user:pass@localhost:3306/films_db
# Update LLM prompt with your column names
```

### Pattern 3: Existing Production Database
```bash
DATABASE_URL=postgresql://user:pass@production-server:5432/prod_db
USE_PRODUCTION_DB=true
# Follow production setup guide
```

## Troubleshooting

### Connection Issues
- ✅ Check DATABASE_URL is correct
- ✅ Verify database server is running
- ✅ Check credentials and permissions
- ✅ Run: `uv run python production/scripts/analyze_database.py`

### Query Not Working
- ✅ Verify LLM prompt has correct table/column names
- ✅ Check SQL examples match your schema
- ✅ Test queries manually in SQL client first

### Schema Mismatch
- ✅ Update field mappings in `schema_mappings.json`
- ✅ Update LLM prompt with actual schema
- ✅ Test with simple queries first

## Key Files to Modify

For custom database integration, you'll typically only need to modify:

1. **`.env`** - Database connection string
2. **`backend/services/query_processor.py`** (lines 106-115) - Database schema description
3. **`production/config/schema_mappings.json`** (optional) - Field mappings if schema differs

## Support

- 📖 Full documentation: `README.md`
- 🚀 Production setup: `production/README.md`
- 🔧 Database adapter: `production/adapters/database_adapter.py`
- 📝 Schema mappings: `production/config/schema_mappings.json`

## The Golden Rule

**The LLM needs to know your database structure!**

If your tables are called `films` instead of `movies`, just update the LLM prompt (line 106-115 in `query_processor.py`) and the system will work with your database! The LLM will generate SQL using your actual table and column names.

That's it! Most integrations only require updating the connection string and the LLM prompt with your actual schema. 🎯
