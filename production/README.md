# Production Setup Guide 🚀

This folder contains all the necessary files and configurations for deploying the NQL Movie Chatbot to production.

## 📁 Folder Structure

```
production/
├── config/                    # Production configurations
│   ├── production.env        # Production environment variables
│   └── schema_mappings.json  # Database schema mappings
├── scripts/                   # Production scripts
│   ├── setup_production.py   # Setup production environment
│   ├── analyze_database.py   # Analyze existing database
│   ├── start_production.py   # Start production server
│   └── test_production.py    # Test production setup
├── adapters/                  # Database adapters
│   ├── database_adapter.py   # Database connection adapter
│   └── production_query_processor.py  # Production query processor
├── examples/                  # Deployment examples
│   ├── docker-compose.yml    # Docker Compose setup
│   └── Dockerfile           # Docker container setup
└── README.md                 # This file
```

## 🚀 Quick Start

### 1. Setup Production Environment

```bash
# Copy production configuration
cp production/config/production.env .env

# Edit .env with your production settings
nano .env

# Run production setup
uv run python production/scripts/setup_production.py
```

### 2. Configure Your Database

#### For Existing Database:
```bash
# Analyze your existing database
uv run python production/scripts/analyze_database.py

# Update schema mappings if needed
nano production/config/schema_mappings.json
```

#### For New Database:
```bash
# Use the provided Docker Compose setup
cd production/examples
docker-compose up -d postgres
```

### 3. Start Production Server

```bash
# Start production server
uv run python production/scripts/start_production.py

# Or use Docker
cd production/examples
docker-compose up -d
```

### 4. Test Production Setup

```bash
# Test the production setup
uv run python production/scripts/test_production.py
```

## 🔧 Configuration

### Environment Variables

Key production environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db
USE_PRODUCTION_DB=true
SCHEMA_TYPE=default

# AI Provider
AI_PROVIDER=openai
OPENAI_API_KEY=your_key

# Security
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=yourdomain.com

# Performance
RATE_LIMIT_PER_MINUTE=100
```

### Database Schema Mappings

The system supports multiple database schemas:

- **default**: Standard movie database schema
- **alternative**: Alternative field naming
- **tmdb**: The Movie Database schema
- **imdb**: IMDB-style schema

## 🐳 Docker Deployment

### Using Docker Compose

```bash
cd production/examples

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f nql-bot

# Stop services
docker-compose down
```

### Using Docker

```bash
# Build image
docker build -f production/examples/Dockerfile -t nql-bot .

# Run container
docker run -p 8000:8000 --env-file .env nql-bot
```

## 📊 Database Integration

### Supported Databases

- **PostgreSQL** (recommended for production)
- **MySQL/MariaDB**
- **SQLite** (for development/testing)

### Schema Detection

The system automatically detects your database schema and maps fields accordingly. You can also manually specify the schema type in your `.env` file.

### Custom Schema

If your database has a custom schema, update the mappings in `production/config/schema_mappings.json`:

```json
{
  "your_schema": {
    "description": "Your custom schema",
    "mappings": {
      "movie_id": "your_id_field",
      "title": "your_title_field",
      "genre": "your_genre_field"
    }
  }
}
```

## 🔍 Monitoring & Logging

### Health Checks

The application provides health check endpoints:

- `GET /health` - Basic health check
- `GET /api/queries/sample` - Test query endpoint

### Logging

Logs are written to:
- Console (for development)
- `logs/app.log` (for production)

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check your `DATABASE_URL` in `.env`
   - Ensure database server is running
   - Verify credentials and permissions

2. **Schema Detection Issues**
   - Run `analyze_database.py` to see your schema
   - Update `schema_mappings.json` if needed
   - Set `SCHEMA_TYPE` manually in `.env`

3. **API Key Issues**
   - Verify your API key is correct
   - Check if you have sufficient credits/quota
   - Ensure the AI provider is set correctly

### Debug Mode

Enable debug mode for troubleshooting:

```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📈 Performance Optimization

### Database Optimization

- Use connection pooling
- Add appropriate indexes
- Optimize queries for your schema

### Caching

- Enable Redis for query caching
- Use database query caching
- Implement response caching

### Scaling

- Use load balancers
- Deploy multiple instances
- Use container orchestration (Kubernetes)

## 🔒 Security

### Production Security Checklist

- [ ] Use strong API keys
- [ ] Enable HTTPS
- [ ] Set up proper CORS
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting
- [ ] Regular security updates

## 📞 Support

For production issues:

1. Check the logs: `docker-compose logs nql-bot`
2. Run diagnostics: `python production/scripts/test_production.py`
3. Verify configuration: `python production/scripts/analyze_database.py`

## 🎯 Next Steps

After successful production deployment:

1. Set up monitoring (Prometheus, Grafana)
2. Configure backup strategies
3. Set up CI/CD pipelines
4. Implement user authentication
5. Add advanced analytics
