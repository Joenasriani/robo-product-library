import sqlite3
import secrets
import hashlib
from datetime import datetime
from pathlib import Path
from src import settings

def _connect():
    Path(settings.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()

def row_to_public(row):
    remaining = max(0, row["credits_total"] - row["credits_used"])
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "plan": row["plan"],
        "credits_total": row["credits_total"],
        "credits_used": row["credits_used"],
        "credits_remaining": remaining,
        "is_active": bool(row["is_active"]),
    }

def init_db():
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS api_clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            api_key_hash TEXT NOT NULL UNIQUE,
            plan TEXT NOT NULL,
            credits_total INTEGER NOT NULL DEFAULT 0,
            credits_used INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS credit_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            delta INTEGER NOT NULL,
            reason TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            tender_id TEXT NOT NULL,
            tender_title TEXT NOT NULL,
            analysis_json TEXT NOT NULL,
            credits_used INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_client(name, email, plan, initial_credits, api_key=None):
    api_key = api_key or f"tr_{secrets.token_urlsafe(24)}"
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO api_clients (name, email, api_key_hash, plan, credits_total, credits_used, is_active, created_at) VALUES (?, ?, ?, ?, ?, 0, 1, ?)",
        (name, email, hash_api_key(api_key), plan, initial_credits, datetime.utcnow().isoformat())
    )
    client_id = cur.lastrowid
    cur.execute(
        "INSERT INTO credit_ledger (client_id, delta, reason, created_at) VALUES (?, ?, ?, ?)",
        (client_id, initial_credits, "initial_allocation", datetime.utcnow().isoformat())
    )
    conn.commit()
    cur.execute("SELECT * FROM api_clients WHERE id = ?", (client_id,))
    row = cur.fetchone()
    conn.close()
    return row_to_public(row), api_key

def seed_demo_client():
    if not settings.DEMO_API_KEY:
        return
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT id FROM api_clients WHERE api_key_hash = ?", (hash_api_key(settings.DEMO_API_KEY),))
    exists = cur.fetchone()
    conn.close()
    if not exists:
        create_client(settings.DEMO_CLIENT_NAME, settings.DEMO_CLIENT_EMAIL, "starter", 25, api_key=settings.DEMO_API_KEY)

def get_client_by_api_key(api_key):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM api_clients WHERE api_key_hash = ?", (hash_api_key(api_key),))
    row = cur.fetchone()
    conn.close()
    return row

def get_client_by_id(client_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM api_clients WHERE id = ?", (client_id,))
    row = cur.fetchone()
    conn.close()
    return row

def list_clients():
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM api_clients ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [row_to_public(r) for r in rows]

def add_credits(client_id, credits, reason):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("UPDATE api_clients SET credits_total = credits_total + ? WHERE id = ?", (credits, client_id))
    cur.execute("INSERT INTO credit_ledger (client_id, delta, reason, created_at) VALUES (?, ?, ?, ?)",
                (client_id, credits, reason, datetime.utcnow().isoformat()))
    conn.commit()
    cur.execute("SELECT * FROM api_clients WHERE id = ?", (client_id,))
    row = cur.fetchone()
    conn.close()
    return row_to_public(row) if row else None

def deduct_credit(client_id, amount=1):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM api_clients WHERE id = ?", (client_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise ValueError("Client not found")
    remaining = row["credits_total"] - row["credits_used"]
    if remaining < amount:
        conn.close()
        raise ValueError("Insufficient credits")
    cur.execute("UPDATE api_clients SET credits_used = credits_used + ? WHERE id = ?", (amount, client_id))
    cur.execute("INSERT INTO credit_ledger (client_id, delta, reason, created_at) VALUES (?, ?, ?, ?)",
                (client_id, -amount, "analysis_request", datetime.utcnow().isoformat()))
    conn.commit()
    cur.execute("SELECT * FROM api_clients WHERE id = ?", (client_id,))
    updated = cur.fetchone()
    conn.close()
    return row_to_public(updated)

def save_analysis(client_id, tender_id, tender_title, analysis_dict):
    import json
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO analysis_history (client_id, tender_id, tender_title, analysis_json, credits_used, created_at) VALUES (?, ?, ?, ?, 1, ?)",
        (client_id, tender_id, tender_title, json.dumps(analysis_dict), datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_history(client_id, limit=50):
    import json
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, tender_id, tender_title, analysis_json, created_at FROM analysis_history WHERE client_id = ? ORDER BY id DESC LIMIT ?",
        (client_id, limit)
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "tender_id": r["tender_id"],
            "tender_title": r["tender_title"],
            "analysis": json.loads(r["analysis_json"]),
            "created_at": r["created_at"],
        }
        for r in rows
    ]
