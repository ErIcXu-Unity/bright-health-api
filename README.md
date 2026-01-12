# Bright Health API

A RESTful health data ingestion and retrieval service built with FastAPI, deployed on Google Cloud Run.

## Features

- **User Health Data Ingestion**: Store health metrics (steps, calories, sleep hours)
- **Data Retrieval**: Query health data with date range filtering and pagination
- **Aggregation**: Calculate total steps, average calories, and average sleep hours
- **Authentication**: API key-based security
- **Rate Limiting**: 60 requests per minute per IP
- **Caching**: In-memory cache with Redis support (Google Cloud Memorystore ready)
- **Auto-generated API Documentation**: Swagger UI at `/docs`

## Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **Database**: Google Cloud Firestore
- **Cache**: In-memory (Redis/Memorystore ready)
- **Deployment**: Google Cloud Run
- **Containerization**: Docker

## Live Demo

**Production URL**: https://bright-health-api-333286589626.australia-southeast1.run.app

**API Key**: Provided separately for security

**Swagger UI**: https://bright-health-api-333286589626.australia-southeast1.run.app/docs

### Quick Test (Cloud Run)

```bash
# Health check (no auth required)
curl https://bright-health-api-333286589626.australia-southeast1.run.app/health

# Create health data (replace YOUR_API_KEY)
curl -X POST "https://bright-health-api-333286589626.australia-southeast1.run.app/users/test-user/health-data" \
  -H "X-API-KEY: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "2026-01-08T08:30:00Z", "steps": 1200, "calories": 450, "sleepHours": 7.5}'

# Get health data
curl "https://bright-health-api-333286589626.australia-southeast1.run.app/users/test-user/health-data?start=01-01-2026&end=31-12-2026" \
  -H "X-API-KEY: YOUR_API_KEY"

# Get summary
curl "https://bright-health-api-333286589626.australia-southeast1.run.app/users/test-user/summary?start=01-01-2026&end=31-12-2026" \
  -H "X-API-KEY: YOUR_API_KEY"
```

### Test Redis Locally

1. **Start Redis with Docker**

   ```bash
   docker run -d -p 6379:6379 --name redis redis
   ```

2. **Configure `.env`**

   ```
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

3. **Run the app**

   ```bash
   uvicorn app.main:app --reload
   ```

4. **Call the summary endpoint** (via Swagger UI or curl)

5. **Verify cache in Redis**

   ```bash
   docker exec -it redis redis-cli
   KEYS *
   # Should show: summary:userId:start:end
   ```

6. **Stop Redis when done**
   ```bash
   docker stop redis && docker rm redis
   ```

## API Endpoints

| Method | Endpoint                      | Description                         |
| ------ | ----------------------------- | ----------------------------------- |
| GET    | `/health`                     | Health check                        |
| POST   | `/users/{userId}/health-data` | Create health record                |
| GET    | `/users/{userId}/health-data` | Get health records with date filter |
| GET    | `/users/{userId}/summary`     | Get aggregated statistics           |

## HTTP Status Codes

| Code | Description                             |
| ---- | --------------------------------------- |
| 200  | Success                                 |
| 201  | Created                                 |
| 400  | Bad Request (invalid date format)       |
| 401  | Unauthorized (invalid API key)          |
| 422  | Validation Error (invalid data)         |
| 429  | Too Many Requests (rate limit exceeded) |

## Setup Instructions

### Prerequisites

- Python 3.11+
- Google Cloud account with Firestore enabled
- Docker (for containerization)
- gcloud CLI (for deployment)

### Local Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd bright-health-api
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google Cloud credentials**

   - Create a service account in Google Cloud Console
   - Download the JSON key file as `service-account.json`
   - Place it in the project root

5. **Create `.env` file**

   ```
   API_KEY=default-dev-key
   GOOGLE_CLOUD_PROJECT=bright-assessment
   GOOGLE_APPLICATION_CREDENTIALS=service-account.json
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

   Note: `REDIS_HOST` is optional. Remove it to use in-memory cache.

6. **Run the application**

   ```bash
   uvicorn app.main:app --reload
   ```

7. **Access the API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

## Running Tests

```bash
pytest
```

With coverage report:

```bash
pytest --cov=app --cov-report=html tests/
```

### Test Coverage

```
Name                      Stmts   Miss  Cover
---------------------------------------------
app/__init__.py               0      0   100%
app/auth.py                   9      0   100%
app/cache.py                 15      0   100%
app/config.py                 8      0   100%
app/database.py              14     14     0%
app/main.py                  15      0   100%
app/models.py                28      0   100%
app/routers/__init__.py       0      0   100%
app/routers/health.py        76      0   100%
---------------------------------------------
TOTAL                       165     14    95%
```

**Note**: `database.py` shows 0% coverage because Firestore is **mocked** in tests. This is intentional:

- Unit tests should be fast and not make network calls
- Tests run without Google Cloud credentials (CI/CD friendly)
- No Firestore read/write costs during testing
- Tests are deterministic and repeatable

The actual Firestore integration is verified through manual testing and the live deployment.

## Deployment to Google Cloud Run

### Build and Push Container

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/bright-health-api
```

### Deploy to Cloud Run

```bash
gcloud run deploy bright-health-api \
  --image gcr.io/YOUR_PROJECT_ID/bright-health-api \
  --platform managed \
  --region australia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars API_KEY=your-production-api-key
```

### Production URL

```
https://bright-health-api-333286589626.australia-southeast1.run.app
```

## API Usage Examples

### Health Check

```bash
curl https://YOUR_URL/health
```

Response:

```json
{ "status": "ok" }
```

### Create Health Data

```bash
curl -X POST "https://YOUR_URL/users/alice/health-data" \
  -H "X-API-KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-01-08T08:30:00Z",
    "steps": 1200,
    "calories": 450,
    "sleepHours": 7.5
  }'
```

Response:

```json
{
  "id": "abc123",
  "userId": "alice",
  "timestamp": "2026-01-08T08:30:00Z",
  "steps": 1200,
  "calories": 450,
  "sleepHours": 7.5
}
```

### Get Health Data

```bash
curl "https://YOUR_URL/users/alice/health-data?start=01-01-2026&end=31-01-2026&page=1" \
  -H "X-API-KEY: your-api-key"
```

Response:

```json
{
  "data": [
    {
      "id": "abc123",
      "userId": "alice",
      "timestamp": "2026-01-08T08:30:00Z",
      "steps": 1200,
      "calories": 450,
      "sleepHours": 7.5
    }
  ],
  "page": 1,
  "total_count": 1,
  "has_more": false
}
```

### Get Summary

```bash
curl "https://YOUR_URL/users/alice/summary?start=01-01-2026&end=31-01-2026" \
  -H "X-API-KEY: your-api-key"
```

Response:

```json
{
  "userId": "alice",
  "startDate": "01-01-2026",
  "endDate": "31-01-2026",
  "totalSteps": 1200,
  "averageCalories": 450.0,
  "averageSleepHours": 7.5
}
```

## Environment Variables

| Variable                         | Description                               | Required   |
| -------------------------------- | ----------------------------------------- | ---------- |
| `API_KEY`                        | Secret key for API authentication         | Yes        |
| `GOOGLE_CLOUD_PROJECT`           | Google Cloud project ID                   | Yes        |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON (local only) | Local only |
| `REDIS_HOST`                     | Redis host for caching (optional)         | No         |
| `REDIS_PORT`                     | Redis port (default: 6379)                | No         |

## Bonus Features Implemented

- [x] **Caching**: In-memory cache with 5-minute TTL, Redis-ready
- [x] **Input Validation**: Pydantic models with constraints (steps >= 0, etc.)
- [x] **Error Handling**: Descriptive HTTP error codes (400, 401, 422, 429)
- [x] **Unit Tests**: 15 tests with 95% coverage
- [x] **Rate Limiting**: 60 requests/minute per IP using slowapi

## Redis/Memorystore Integration

The caching layer supports Google Cloud Memorystore (Redis). To enable:

1. Create a Memorystore Redis instance
2. Set up Serverless VPC Access connector
3. Configure Cloud Run with VPC connector
4. Set environment variables:
   ```
   REDIS_HOST=your-redis-ip
   REDIS_PORT=6379
   ```

The application automatically falls back to in-memory caching when Redis is unavailable.

## Project Structure

```
bright-health-api/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── config.py         # Configuration settings
│   ├── auth.py           # API key authentication
│   ├── database.py       # Firestore connection
│   ├── models.py         # Pydantic models
│   ├── cache.py          # Caching layer (memory/Redis)
│   └── routers/
│       ├── __init__.py
│       └── health.py     # Health data endpoints
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Pytest fixtures
│   └── test_health.py    # Unit tests
├── Dockerfile
├── requirements.txt
└── README.md
```

## License

This project was created as a technical assessment.
