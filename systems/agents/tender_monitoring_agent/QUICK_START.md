# Tender Monitoring Agent - Quick Start

## Prerequisites
- Docker Engine + Docker Compose plugin
- One valid provider key configured in `.env` (OpenAI/Anthropic/Gemini/local OpenAI-compatible endpoint)

## 1) Configure
```bash
cp .env.example .env
```
Set at minimum: `LLM_PROVIDER`, `LLM_MODEL`, matching provider key, and `ADMIN_TOKEN`.

## 2) Start
```bash
docker compose up -d --build
```

## 3) Run smoke test
```bash
ADMIN_TOKEN=change-admin-token ./validation/smoke_test.sh
```

## 4) Open dashboard
- http://127.0.0.1:8007

## Troubleshooting
- `502`/`503` on analyze endpoints: provider key/model in `.env` is missing/invalid.
- Port busy: change `PORT` in `.env`, then restart.

## Stop / reset
```bash
docker compose down
# full cleanup
docker compose down -v
```
