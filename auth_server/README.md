# CAILculator Auth Server (v1.4.4)

FastAPI backend for API key management and usage tracking.

**MILESTONE (April 2026):** This server now supports v1.4.4 clients using formally verified mathematical constants from `ChavezTransform_genuine.lean`.

## Deployment (Railway)

This server is designed to deploy on Railway with automatic PostgreSQL provisioning.

### Setup

1. **Create new Railway project** from GitHub repo
2. **Add PostgreSQL database** (Railway provision)
3. **Configure service**:
   - Root directory: `auth_server`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Deploy** - Railway auto-deploys on push

### Environment Variables

Railway sets these automatically:
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Server port

### API Endpoints

#### Health Check
```
GET /
GET /health
```

#### User Signup
```
POST /signup
{
  "email": "user@example.com",
  "name": "User Name"
}
```

#### Validate API Key
```
POST /validate
{
  "api_key": "cail_..."
}
```

#### Log Usage
```
POST /log-usage
{
  "api_key": "cail_...",
  "tool_name": "test_zero_divisor",
  "dimension": 32
}
```

#### Get Usage Stats
```
GET /usage/{api_key}
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up local PostgreSQL database
createdb cailculator_dev

# Copy environment template
cp .env.example .env

# Run server
uvicorn main:app --reload
```

Server runs at: http://localhost:8000

API docs at: http://localhost:8000/docs

## Subscription Tiers

- **Student**: $4.99/month - 1,000 requests
- **Teacher**: $9.99/month - 5,000 requests
- **Indie**: $49/month - 15,000 requests
- **Team**: $250/month - 100,000 requests
- **Enterprise**: Custom pricing (starting at $3,000/month) - Unlimited

