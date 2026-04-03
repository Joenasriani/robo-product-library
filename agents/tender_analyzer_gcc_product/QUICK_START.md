# Tender Analyzer GCC — Quick Start

## 1. Install

```bash
pip install -r requirements.txt
```

## 2. Configure

```bash
cp .env.example .env
```

Set at minimum:
- `LLM_PROVIDER`
- matching provider API key
- `ADMIN_TOKEN`
- `DEMO_API_KEY`

## 3. Run

```bash
python -m src.main
```

## 4. Open dashboard

Open `http://localhost:8000`

## 5. Admin: create buyer key

```bash
curl -X POST http://localhost:8000/api/v1/admin/clients \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: change-admin-token" \
  -d '{"name":"Acme GCC","email":"ops@acme.com","plan":"starter","initial_credits":100}'
```
