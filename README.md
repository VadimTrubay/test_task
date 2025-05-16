# test_task


A FastAPI service that predicts country of origin based on names using Nationalize.io and REST Countries APIs.

## Features

- Predict country of origin for a given name
- Get top 5 most frequent names for a country
- Caching of results to minimize external API calls
- JWT authentication for API access

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | Database connection URL | postgresql://user:pass@host:port/db |
| SECRET_KEY | Secret key for JWT token generation | your-secret-key-here |
| ALGORITHM | Algorithm for JWT | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration time | 30 |

## API Endpoints

### `/names/`
- **GET**: Get country predictions for a name
- Parameters: `name` (required)
- Authentication: Required

### `/popular-names/`
- **GET**: Get top 5 names for a country
- Parameters: `country` (required, 2-letter code)
- Authentication: Required

### `/token`
- **POST**: Get JWT token
- Parameters: `username`, `password`
- Authentication: None

## Running the Service

1. Copy `.env.example` to `.env` and configure variables
2. Run `docker-compose up --build`
3. Access API docs at `http://localhost:8000/docs`

## Improvements

1. **Caching**: Added caching of name results for 1 day to reduce external API calls
2. **Authentication**: Implemented JWT auth for API security
3. **Error Handling**: Comprehensive error handling for external API failures
4. **Database Design**: Normalized database structure for efficient queries
5. **Async**: Used async/await for better performance with external APIs

Possible downsides:
- Additional complexity from authentication
- Caching might return slightly stale data (1 day max)