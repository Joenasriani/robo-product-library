import sqlite3
import secrets
import hashlib
import json
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
    return {"id": row["id"], "name": row["name"], "email": row["email"], "plan": row["plan"],
            "credits_total": row["credits_total"], "credits_used": row["credits_used"],
            "credits_remaining": remaining, "is_active": bool(row["is_active"])}

def init_db():
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS api_clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT,
        api_key_hash TEXT NOT NULL UNIQUE, plan TEXT NOT NULL,
        credits_total INTEGER NOT NULL DEFAULT 0, credits_used INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS credit_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER NOT NULL,
        delta INTEGER NOT NULL, reason TEXT NOT NULL, created_at TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS agent_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
        description TEXT NOT NULL, version TEXT NOT NULL DEFAULT "1.0.0", category TEXT NOT NULL,
        price_aed REAL NOT NULL, status TEXT NOT NULL DEFAULT "active",
        file_size_mb REAL, requirements_json TEXT NOT NULL DEFAULT "[]",
        included_files_json TEXT NOT NULL DEFAULT "[]", created_at TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS entitlements (
        id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER NOT NULL, product_id INTEGER NOT NULL,
        granted_at TEXT NOT NULL, expires_at TEXT, status TEXT NOT NULL DEFAULT "active",
        UNIQUE(client_id, product_id))""")
    conn.commit()
    _seed_products(conn)
    conn.close()

def _seed_products(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM agent_products")
    if cur.fetchone()[0] > 0:
        return
    products = [
        ("tender-analyzer-gcc", "Tender Analyzer GCC", "AI-powered GCC tender evaluation engine. Scores, classifies and recommends actions for government procurement opportunities.", "2.0.0", "Analysis", 1200.0, 1.2, ["Python 3.11+", "FastAPI", "OpenAI API key"], ["src/", "frontend/", "Dockerfile", "docker-compose.yml", "README.md"]),
        ("sales-outreach-agent", "Sales Outreach Agent", "Generate tailored B2B outreach sequences for GCC/Middle East enterprise sales.", "1.0.0", "Sales", 900.0, 0.8, ["Python 3.11+", "FastAPI", "OpenAI API key"], ["src/", "frontend/", "Dockerfile", "docker-compose.yml", "README.md"]),
        ("lead-research-agent", "Lead Research Agent", "Research target companies, classify opportunities, and prepare structured lead intelligence.", "1.0.0", "Sales", 900.0, 0.8, ["Python 3.11+", "FastAPI", "OpenAI API key"], ["src/", "frontend/", "Dockerfile", "docker-compose.yml", "README.md"]),
    ]
    for slug, name, desc, ver, cat, price, size, reqs, files in products:
        cur.execute(
            "INSERT INTO agent_products (slug, name, description, version, category, price_aed, file_size_mb, requirements_json, included_files_json, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (slug, name, desc, ver, cat, price, size, json.dumps(reqs), json.dumps(files), datetime.utcnow().isoformat())
        )
    conn.commit()

def create_client(name, email, plan, initial_credits, api_key=None):
    api_key = api_key or f"rm_{secrets.token_urlsafe(24)}"
    conn = _connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO api_clients (name, email, api_key_hash, plan, credits_total, credits_used, is_active, created_at) VALUES (?,?,?,?,?,0,1,?)",
                (name, email, hash_api_key(api_key), plan, initial_credits, datetime.utcnow().isoformat()))
    client_id = cur.lastrowid
    cur.execute("INSERT INTO credit_ledger (client_id, delta, reason, created_at) VALUES (?,?,?,?)",
                (client_id, initial_credits, "initial_allocation", datetime.utcnow().isoformat()))
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
    if not cur.fetchone():
        conn.close()
        create_client(settings.DEMO_CLIENT_NAME, settings.DEMO_CLIENT_EMAIL, "starter", 0, api_key=settings.DEMO_API_KEY)
    else:
        conn.close()

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
    cur.execute("INSERT INTO credit_ledger (client_id, delta, reason, created_at) VALUES (?,?,?,?)",
                (client_id, credits, reason, datetime.utcnow().isoformat()))
    conn.commit()
    cur.execute("SELECT * FROM api_clients WHERE id = ?", (client_id,))
    row = cur.fetchone()
    conn.close()
    return row_to_public(row) if row else None

def list_products(active_only=True):
    conn = _connect()
    cur = conn.cursor()
    if active_only:
        cur.execute("SELECT * FROM agent_products WHERE status = 'active' ORDER BY id")
    else:
        cur.execute("SELECT * FROM agent_products ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return [_product_row(r) for r in rows]

def get_product(product_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM agent_products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return _product_row(row) if row else None

def _product_row(row):
    return {"id": row["id"], "slug": row["slug"], "name": row["name"], "description": row["description"],
            "version": row["version"], "category": row["category"], "price_aed": row["price_aed"],
            "status": row["status"], "file_size_mb": row["file_size_mb"],
            "requirements": json.loads(row["requirements_json"] or "[]"),
            "included_files": json.loads(row["included_files_json"] or "[]")}

def create_product(slug, name, description, version, category, price_aed, requirements, included_files):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO agent_products (slug, name, description, version, category, price_aed, requirements_json, included_files_json, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (slug, name, description, version, category, price_aed, json.dumps(requirements), json.dumps(included_files), datetime.utcnow().isoformat()))
    conn.commit()
    product_id = cur.lastrowid
    conn.close()
    return get_product(product_id)

def grant_entitlement(client_id, product_id, expires_at=None):
    conn = _connect()
    cur = conn.cursor()
    try:
        cur.execute("INSERT OR REPLACE INTO entitlements (client_id, product_id, granted_at, expires_at, status) VALUES (?,?,?,?,?)",
                    (client_id, product_id, datetime.utcnow().isoformat(), expires_at, "active"))
        conn.commit()
        entitlement_id = cur.lastrowid
    finally:
        conn.close()
    return entitlement_id

def get_entitlements(client_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""SELECT e.id, e.product_id, p.name as product_name, e.granted_at, e.expires_at, e.status
                   FROM entitlements e JOIN agent_products p ON e.product_id = p.id
                   WHERE e.client_id = ? ORDER BY e.id DESC""", (client_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_entitlement(client_id, product_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM entitlements WHERE client_id = ? AND product_id = ? AND status = 'active'",
                (client_id, product_id))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def list_all_entitlements():
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""SELECT e.*, p.name as product_name, c.name as client_name
                   FROM entitlements e JOIN agent_products p ON e.product_id = p.id
                   JOIN api_clients c ON e.client_id = c.id ORDER BY e.id DESC""")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
