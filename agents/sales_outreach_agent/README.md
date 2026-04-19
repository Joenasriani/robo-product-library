# Sales Outreach Agent

> **Status:** testing

## Overview
Research B2B leads and generate tailored outreach sequences for GCC/Middle East sales.

## Quick Start
See [QUICK_START.md](QUICK_START.md)

## Product Readiness
- Deliverables: source API/runtime + frontend + deployment files (see repository tree)
- Setup expectations: `.env` values + API/admin keys ([QUICK_START.md](QUICK_START.md))
- Commercial boundaries: [LIMITATIONS.md](LIMITATIONS.md)
- Support & fulfillment: [SUPPORT.md](SUPPORT.md)

## API
- `GET /health` — Health check
- `GET /api/v1/account/me` — Account info
- `POST /api/v1/*/analyze` — Run analysis (costs 1 credit)
- `GET /api/v1/*/history` — Analysis history
- `POST /api/v1/admin/clients` — Create client (admin)
- `POST /api/v1/admin/credits/add` — Add credits (admin)

## Port
Default: `8001`

## Auth
All analysis endpoints require `X-API-Key` header.
Admin endpoints require `X-Admin-Token` header.
