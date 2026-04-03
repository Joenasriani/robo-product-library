#!/usr/bin/env python3
import os
import sys
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("DEMO_API_KEY", "")
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

def ok(v, label):
    print(f"[{'PASS' if v else 'FAIL'}] {label}")
    return v

def test_health():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        return ok(r.status_code == 200, "GET /health")
    except Exception:
        return ok(False, "GET /health")

def test_account():
    try:
        r = requests.get(f"{BASE_URL}/api/v1/account/me", headers=HEADERS, timeout=5)
        return ok(r.status_code == 200, "GET /api/v1/account/me")
    except Exception:
        return ok(False, "GET /api/v1/account/me")

def test_analysis():
    try:
        payload = {
            "id":"test-001",
            "title":"Cloud Infrastructure Migration",
            "description":"Migration of on-premise systems to cloud with support SLA.",
            "issuer":"Dubai Municipality",
            "country":"UAE",
            "sector":"IT"
        }
        r = requests.post(f"{BASE_URL}/api/v1/tenders/analyze", headers={**HEADERS, "Content-Type":"application/json"}, json=payload, timeout=60)
        if r.status_code != 200:
            return ok(False, "POST /api/v1/tenders/analyze")
        a = r.json()[0]["analysis"]
        return ok(a["recommended_action"] in {"pursue","review","skip"}, "POST /api/v1/tenders/analyze")
    except Exception:
        return ok(False, "POST /api/v1/tenders/analyze")

if __name__ == "__main__":
    results = [test_health(), test_account(), test_analysis()]
    sys.exit(0 if all(results) else 1)
