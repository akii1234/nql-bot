# Using NQL Bot with Your Existing Database 🗄️

**TL;DR: Just set your DATABASE_URL and it works! MCP does the rest.** ✨

## Quick Setup (3 Steps)

### Step 1: Clone and Install
```bash
git clone https://github.com/akhiltripathi/nql-bot.git
cd nql-bot
uv sync
```

### Step 2: Configure Your Database
```bash
# Copy environment file
cp env.example .env

# Edit .env
nano .env
```

**Add these lines:**
```bash
# Your database connection
DATABASE_URL=postgresql://user:pass@host:5432/your_existing_db

# Tell the app to use existing database (don't create tables)
USE_PRODUCTION_DB=true
SKIP_TABLE_CREATION=true
```

### Step 3: Start the App
```bash
./start.sh
```

**That's it!** MCP will:
- ✅ Connect to your database
- ✅ Read your actual schema
- ✅ Adapt to your table/column names
- ✅ Work immediately!

## How It Works

### Your Database Has Different Schema

**Example: Your database**
```sql
Table: film_catalog
  - film_id (INT)
  - film_name (VARCHAR)
  - category (VARCHAR)
  - released_year (INT)
  - imdb_rating (DECIMAL)

Table: view_statistics  
  - stat_id (INT)
  - film_id (INT)
  - view_date (DATE)
  - view_count (INT)
```

### What MCP Does Automatically

**1. Detects Your Schema:**
```
Found tables: film_catalog, view_statistics
Found columns: film_id, film_name, category, released_year...
```

**2. Tells LLM:**
```
"Your database has:
Table: film_catalog
  - film_id (INT)
  - film_name (VARCHAR)
  - category (VARCHAR)
  ..."
```

**3. User Asks:**
```
"Show me action movies from 2024"
```

**4. LLM Generates (using YOUR schema):**
```sql
SELECT * FROM film_catalog 
WHERE category='Action' AND released_year=2024
```

**5. Returns Results!** ✅

## What You DON'T Need to Do

❌ Change any code files  
❌ Update models  
❌ Create field mappings  
❌ Modify prompts  
❌ Write custom SQL logic  

## What the App WILL NOT Do

❌ Create new tables in your database  
❌ Modify your existing schema  
❌ Migrate or change your data  
❌ Force you to use our table/column names  

## Environment Variables for Existing Databases

```bash
# Required
DATABASE_URL=your_database_connection_string

# Recommended for existing databases
USE_PRODUCTION_DB=true          # Prevents table creation
SKIP_TABLE_CREATION=true        # Extra safety flag

# Optional (MCP doesn't need these, but kept for documentation)
SCHEMA_TYPE=custom              # Describe your schema type
```

## Testing Your Integration

After starting the app:

1. Open http://localhost:8501
2. Enter your API key
3. Try simple queries:
   - "How many records are in the database?"
   - "Show me all data from [your_table_name]"
   - "List the first 5 entries"

MCP will generate SQL using your actual table names!

## Troubleshooting

### Issue: "Table not found"
- Check DATABASE_URL is correct
- Verify database is running
- Test connection manually

### Issue: "Column not found"
- MCP should handle this automatically
- Run `analyze_database.py` to see what MCP detected
- Check if LLM has network access

### Issue: "Tables created when they shouldn't be"
- Set `USE_PRODUCTION_DB=true` in .env
- Set `SKIP_TABLE_CREATION=true` in .env
- Restart the application

## Advanced: Completely Different Schema

Even if your database is COMPLETELY different:
- Different table names
- Different column names  
- Different structure
- Different relationships

**MCP will still work!**

Just:
1. Set `DATABASE_URL`
2. Set `USE_PRODUCTION_DB=true`
3. Start the app
4. MCP adapts automatically

The LLM will figure out how to query your specific schema! 🚀

## Summary

**Old Approach (Without MCP):**
- Required manual configuration
- Needed field mappings
- Had to update prompts
- Complex integration process

**New Approach (With MCP):**
- Zero configuration needed
- Automatic schema detection
- Dynamic adaptation
- Works immediately!

**Just point to your database and go!** 🎯✨
