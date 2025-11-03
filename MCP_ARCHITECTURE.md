# Model Context Protocol (MCP) Architecture 🔌

## What is MCP?

**Model Context Protocol (MCP)** is an approach that gives LLMs direct, structured access to external resources like databases, APIs, and tools.

## Why We Use MCP for NQL Bot

### Traditional Approach (What We Had Before):
```
User Query → Parse Intent → Generate SQL → Execute → Return Results
              ↓ (error-prone)  ↓ (rigid)
           JSON structure    Hard-coded logic
```

**Problems:**
- ❌ LLM doesn't see actual database schema
- ❌ Requires constant prompt updates
- ❌ Breaks when schema changes
- ❌ Complex parsing logic prone to errors

### MCP Approach (What We Have Now):
```
User Query → LLM (with database context) → Generate SQL → Execute → Return Results
                    ↓
              Real database schema
              Sample data
              Dynamic context
```

**Benefits:**
- ✅ LLM sees actual database structure
- ✅ Adapts automatically to schema changes
- ✅ Better SQL generation
- ✅ Fewer errors and edge cases

## How MCP Works in NQL Bot

### 1. Dynamic Schema Detection

```python
# MCP automatically detects your database schema
schema_info = {
    "movies": [
        {"name": "id", "type": "INTEGER", "nullable": False},
        {"name": "title", "type": "TEXT", "nullable": False},
        {"name": "genre", "type": "TEXT", "nullable": True},
        ...
    ]
}
```

### 2. Real-Time Context

The LLM receives:
- **Database schema** - Actual table and column names
- **Sample data** - A few rows for reference
- **Column types** - Know what's INTEGER, TEXT, DATE, etc.

### 3. Better SQL Generation

**Before (Manual Parsing):**
```python
if "action movies" in query:
    filters["genre"] = "action"  # Might miss variations
```

**After (MCP):**
```python
# LLM sees schema and generates:
SELECT * FROM movies WHERE genre='Action'  # Correct every time
```

## Architecture Components

### MCPQueryProcessor
**Location:** `backend/services/mcp_query_processor.py`

**Key Methods:**
- `_get_database_schema()` - Dynamically inspects database
- `_format_schema_for_prompt()` - Formats schema for LLM
- `_get_sample_data()` - Provides context examples
- `execute_sql()` - Safely executes generated SQL

### Flow Diagram

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Is Conversation?│
└────┬──────┬─────┘
     │      │
    Yes    No
     │      │
     ▼      ▼
┌─────┐  ┌──────────────────┐
│Reply│  │ MCP Context      │
└─────┘  │ - Schema         │
         │ - Sample Data    │
         │ - Column Types   │
         └────────┬─────────┘
                  │
                  ▼
         ┌────────────────┐
         │ LLM Generates  │
         │ SQL Query      │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │ Execute SQL    │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │ Format Answer  │
         │ Return Results │
         └────────────────┘
```

## Key Advantages

### 1. Works with Any Database Schema

**Your database has different column names?**
- ✅ MCP detects them automatically
- ✅ LLM uses actual column names
- ✅ No manual mapping needed!

Example:
```
Your Schema:
- films table with "film_title" instead of "title"

MCP automatically provides:
"Table: films
  - film_id (INTEGER)
  - film_title (TEXT)
  ..."

LLM generates:
SELECT * FROM films WHERE film_title LIKE '%Action%'
```

### 2. Handles Schema Changes

**Database schema updated?**
- ✅ MCP detects changes on startup
- ✅ LLM uses new schema automatically
- ✅ No code changes needed!

### 3. Better Error Messages

**Query fails?**
- ✅ MCP knows actual column names
- ✅ Can suggest corrections
- ✅ More helpful feedback

### 4. Reduced Maintenance

**Before MCP:**
- Need to update prompts for every schema change
- Need to maintain field mappings
- Need to handle edge cases manually

**After MCP:**
- Schema detected automatically
- LLM adapts to changes
- Fewer edge cases

## Comparison: Old vs New Approach

### Old Approach (Commented Out)
**Files:** `backend/services/query_processor.py` (old code commented)

**How it worked:**
1. Parse query → Extract entities
2. Map entities → Filters/intents
3. Generate SQL from rules
4. Execute

**Problems:**
- Complex parsing logic
- Many edge cases
- Constant fixes needed

### New MCP Approach
**Files:** `backend/services/mcp_query_processor.py`

**How it works:**
1. Get database schema dynamically
2. Give LLM full context
3. LLM generates SQL
4. Execute and format

**Benefits:**
- Simple architecture
- LLM handles complexity
- Works with any schema

## Integration with Your Own Database

### Step 1: Set Database URL
```bash
DATABASE_URL=postgresql://user:pass@host:port/your_db
```

### Step 2: Start Application
```bash
./start.sh
```

### Step 3: MCP Does the Rest!
- ✅ Detects your schema automatically
- ✅ Inspects table and column names
- ✅ Gets sample data for context
- ✅ LLM generates SQL using YOUR schema
- ✅ Works immediately!

## Technical Details

### Schema Inspection

Uses SQLAlchemy's `inspect()` to get:
- Table names
- Column names and types
- Nullable constraints
- Primary/foreign keys

```python
inspector = inspect(engine)
for table_name in inspector.get_table_names():
    columns = inspector.get_columns(table_name)
    # Provide to LLM
```

### Sample Data Context

Provides 2-3 sample rows to help LLM understand:
- Data formats
- Example values
- Relationships

### Safe SQL Execution

- Uses parameterized queries
- Validates results
- Handles errors gracefully
- Returns structured data

## Future Enhancements

With MCP foundation, we can add:
- 🔮 **Multi-database support** - Query multiple databases
- 🔗 **Relationship detection** - Auto-detect foreign keys
- 📊 **Smart suggestions** - Recommend queries based on schema
- 🛡️ **Query validation** - Validate before execution
- 📈 **Performance optimization** - Index suggestions

## Code Structure

### Old Code (Preserved, Not Used)
- `backend/services/query_processor.py` - Complex parsing approach
- `backend/services/direct_query_processor.py` - Simple direct approach
- `backend/routers/queries.py` - Old router
- `backend/routers/direct_queries.py` - Direct router

### New MCP Code (Active)
- `backend/services/mcp_query_processor.py` - MCP implementation
- `backend/routers/mcp_queries.py` - MCP router
- `main.py` - Uses MCP router

All old code is **commented out and preserved** for reference!

## Summary

**MCP gives the LLM "eyes" to see your actual database**, making it smarter and more reliable. Instead of guessing your schema, it knows exactly what tables and columns you have, and generates perfect SQL every time! 🎯✨
