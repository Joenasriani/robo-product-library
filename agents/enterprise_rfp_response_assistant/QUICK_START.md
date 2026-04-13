# Enterprise RFP Response Assistant - Quick Start

## Prerequisites
- Docker & Docker Compose
- OpenAI API key (or Anthropic/Gemini)

## Setup

```bash
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY and ADMIN_TOKEN
docker-compose up -d
```

## Test

```bash
# Health check
curl http://localhost:8003/health

# Create a client
curl -X POST http://localhost:8003/api/v1/admin/clients \
  -H "X-Admin-Token: YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","plan":"starter","initial_credits":50}'

# Use the returned api_key for analysis requests
curl http://localhost:8003/api/v1/account/me \
  -H "X-API-Key: YOUR_API_KEY"
```

## Dashboard
Open http://localhost:8003 in your browser.
