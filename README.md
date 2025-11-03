# NQL Movie Chatbot 🎬

A Natural Query Language (NQL) chatbot that allows users to query movie databases using natural language. Built with FastAPI, LangChain, Model Context Protocol (MCP), and Streamlit.

## Features

- **🎯 User-Friendly Setup**: No configuration files needed - just enter your name and API key
- **🔐 Secure Session Management**: API keys are stored securely and automatically removed on logout
- **🤖 Multiple AI Providers**: Choose between OpenAI GPT or Google Gemini 2.0 Flash
- **🔌 MCP Integration**: Uses Model Context Protocol for direct database access
- **💬 Natural Language Processing**: Ask questions about movies in plain English
- **🗣️ Conversational Interface**: Say "hello", "hi", "what can you do?" for natural interactions
- **🧠 Dynamic Schema Detection**: Automatically adapts to your database structure
- **🎬 Flexible Database Support**: Works with any movie database
- **⚡ Real-time Results**: Fast API responses with query execution metrics
- **🌐 Beautiful Web Interface**: Modern Streamlit frontend with chat history
- **🔄 Session Persistence**: Your conversation continues until you logout

## Example Queries

### 🗣️ Conversational
- "Hello!" / "Hi there!" / "Hey!"
- "What can you do?"
- "How are you?"
- "Thanks, bye!"

### 🎬 Movie Queries
- "Find me the movies which was most watched between 01-01-2025 to 03-02-2025"
- "Show me the highest rated action movies"
- "What are the most popular movies by Christopher Nolan?"
- "Find movies released in 2024 with rating above 8.0"
- "Show me the longest movies in the database"

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, LangChain
- **Frontend**: Streamlit
- **Database**: SQLite (easily configurable for PostgreSQL)
- **AI/ML**: OpenAI GPT, LangChain
- **Package Management**: uv (ultra-fast Python package manager)

## Project Structure

```
nql-bot/
├── backend/
│   ├── models/          # SQLAlchemy database models
│   ├── services/        # LangChain query processing services
│   ├── routers/         # FastAPI route handlers
│   └── utils/           # Database and utility functions
├── frontend/            # Streamlit web interface
├── scripts/             # Database population scripts
├── data/                # SQLite database files
├── main.py              # FastAPI application entry point
├── pyproject.toml       # Project dependencies and configuration
└── README.md
```

## Quick Start

### 1. Prerequisites

- Python 3.11+
- uv package manager ([install here](https://github.com/astral-sh/uv))
- OpenAI or Google Gemini API key

### 2. Installation & Setup

```bash
# Clone the repository
git clone https://github.com/akhiltripathi/nql-bot.git
cd nql-bot

# Install dependencies
uv sync

# Start the application (this will auto-create database with 100 sample movies)
./start.sh
```

That's it! The script will:
- ✅ Install all dependencies
- ✅ Create `.env` file automatically
- ✅ Populate database with sample data if not exists
- ✅ Start both backend and frontend servers

### 3. First Time Setup in Browser

1. **Open** `http://localhost:8501` in your browser
2. **Enter your name**
3. **Choose AI provider** (OpenAI or Gemini)
4. **Enter your API key** (keys stored securely in session, removed on logout)
5. **Start chatting!** 

### 4. Get Your API Key

#### Google Gemini (Recommended - Free tier available):
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

#### OpenAI:
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in
3. Click "Create new secret key"
4. Copy the key

### 5. Start Using!

Ask questions like:
- "How many movies do you have?"
- "Show me action movies from 2024"
- "Find most watched movies of 2025"
- "What are the highest rated drama movies?"

### 6. API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Usage

### API Endpoints

- `POST /api/queries/process` - Process natural language queries
- `GET /api/queries/sample` - Get sample movies
- `GET /health` - Health check

### Example API Request

```bash
curl -X POST "http://localhost:8000/api/queries/process" \
     -H "Content-Type: application/json" \
     -d '{"query": "Find me the movies which was most watched between 01-01-2025 to 03-02-2025"}'
```

## Configuration

### Environment Variables

- `AI_PROVIDER` - AI provider to use: "openai" or "gemini" (default: gemini)
- `OPENAI_API_KEY` - Your OpenAI API key (required if using OpenAI)
- `GEMINI_API_KEY` - Your Google Gemini API key (required if using Gemini)
- `DATABASE_URL` - Database connection string (default: SQLite)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `DEBUG` - Debug mode (default: True)

### Getting API Keys

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in to your account
3. Click "Create new secret key"
4. Copy the generated key

## Development

### Adding New Query Types

1. Update the `QueryIntent` model in `backend/services/query_processor.py`
2. Modify the system prompt to handle new query patterns
3. Update the SQL generation logic in `generate_sql_query()`

### Database Schema

The application uses the following main tables:
- `movies` - Movie information and metadata
- `movie_viewership` - Viewership statistics over time
- `users` - User accounts (for future features)
- `user_queries` - Query history and analytics

### Testing

```bash
# Run tests
uv run pytest

# Run linting
uv run black .
uv run flake8 .
uv run mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Production Deployment

For production deployment with existing databases, see the [Production Setup Guide](production/README.md).

### Quick Production Setup

```bash
# Setup production environment
cp production/config/production.env .env
# Edit .env with your production settings

# Analyze your existing database
uv run python production/scripts/analyze_database.py

# Start production server
uv run python production/scripts/start_production.py
```

## Roadmap

- [ ] Support for more complex queries (comparisons, aggregations)
- [ ] User authentication and query history
- [ ] Movie recommendation engine
- [ ] Integration with real movie databases (TMDB, OMDb)
- [ ] Advanced analytics and insights
- [ ] Mobile app interface
