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
        api_key_hash TEXT NOT NULL UNIQUE, plan TEXT NOT NULL DEFAULT "free",
        credits_total INTEGER NOT NULL DEFAULT 0, credits_used INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS credit_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER NOT NULL,
        delta INTEGER NOT NULL, reason TEXT NOT NULL, created_at TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS protocol_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, slug TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
        category TEXT NOT NULL, region TEXT NOT NULL DEFAULT "GCC",
        description TEXT NOT NULL, price_aed REAL NOT NULL, status TEXT NOT NULL DEFAULT "active",
        version TEXT NOT NULL DEFAULT "1.0.0", risk_level TEXT NOT NULL DEFAULT "medium",
        hardware_requirements_json TEXT NOT NULL DEFAULT "[]",
        included_files_json TEXT NOT NULL DEFAULT "[]",
        use_cases_json TEXT NOT NULL DEFAULT "[]",
        limitations_json TEXT NOT NULL DEFAULT "[]",
        support_mode TEXT NOT NULL DEFAULT "inquiry_and_manual_fulfillment",
        delivery_type TEXT NOT NULL DEFAULT "download", created_at TEXT NOT NULL)""")
    _ensure_protocol_products_columns(cur)
    cur.execute("""CREATE TABLE IF NOT EXISTS protocol_inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER NOT NULL,
        buyer_name TEXT NOT NULL, buyer_email TEXT NOT NULL, buyer_organization TEXT NOT NULL,
        message TEXT, deployment_context TEXT,
        status TEXT NOT NULL DEFAULT "pending", created_at TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS protocol_entitlements (
        id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER NOT NULL,
        inquiry_id INTEGER, buyer_email TEXT NOT NULL,
        granted_at TEXT NOT NULL, expires_at TEXT, status TEXT NOT NULL DEFAULT "active",
        delivery_notes TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS protocol_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, inquiry_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL, buyer_email TEXT NOT NULL,
        amount_aed REAL NOT NULL, status TEXT NOT NULL DEFAULT "approved",
        created_at TEXT NOT NULL)""")
    conn.commit()
    _seed_products(conn)
    conn.close()

def _ensure_protocol_products_columns(cur):
    cur.execute("PRAGMA table_info(protocol_products)")
    columns = {row[1] for row in cur.fetchall()}
    if "use_cases_json" not in columns:
        cur.execute("ALTER TABLE protocol_products ADD COLUMN use_cases_json TEXT NOT NULL DEFAULT '[]'")
    if "limitations_json" not in columns:
        cur.execute("ALTER TABLE protocol_products ADD COLUMN limitations_json TEXT NOT NULL DEFAULT '[]'")
    if "support_mode" not in columns:
        cur.execute("ALTER TABLE protocol_products ADD COLUMN support_mode TEXT NOT NULL DEFAULT 'inquiry_and_manual_fulfillment'")

def _seed_products(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM protocol_products")
    if cur.fetchone()[0] > 0:
        return
    products = [
        ("gcc-royal-protocol-pack", "GCC Royal Protocol Pack", "Royal & Government", "GCC",
         "Complete behavioral protocol for robots operating in royal courts, government palaces, and high-level state events in GCC countries. Includes deference postures, VIP recognition behaviors, ceremonial movement sequences, and restricted zone awareness.",
         4200.0, "1.2.0", "high",
         ["Universal Robots UR5/UR10", "Boston Dynamics Spot", "Custom humanoid platforms"],
         ["gcc_royal_protocol.yaml", "posture_library/", "vip_recognition_model.pkl", "README.md", "integration_guide.pdf"],
         ["Government reception", "Executive arrival protocols", "VIP hosting"],
         ["Requires operator approval for authority-sensitive contexts", "Does not replace a human protocol officer"],
         "Inquiry-only with manual delivery after approval"),
        ("gcc-hotel-concierge-protocol", "GCC Hotel Concierge Protocol", "Hospitality", "GCC",
         "Hospitality-grade behavioral pack for robot concierges in luxury UAE and KSA hotels. Covers greeting rituals, multilingual interaction (Arabic/English), luggage assistance cues, prayer time awareness, and halal dining guidance.",
         2800.0, "1.1.0", "low",
         ["Softbank Pepper", "PAL Robotics ARI", "Any ROS2-compatible platform"],
         ["concierge_behaviors.yaml", "language_packs/", "hotel_zones_config.json", "README.md"],
         ["Hotel lobbies", "Guest check-in support", "Concierge routing"],
         ["Does not process bookings or payments autonomously", "Does not replace front-desk staff"],
         "Inquiry-only with manual delivery after approval"),
        ("gcc-royal-privacy-protocol-v1", "GCC Royal Privacy Protocol v1", "Privacy & Security", "GCC",
         "Privacy-first behavioral constraints for robots deployed near royal family members, government officials, and sensitive diplomatic environments. Implements camera deactivation zones, conversation non-recording policies, and secure data handling.",
         3900.0, "1.0.1", "high",
         ["Any camera-equipped robot platform", "ROS2 middleware"],
         ["privacy_zones.yaml", "camera_control_module/", "audit_logging_config.json", "README.md", "compliance_checklist.pdf"],
         ["Government reception", "VIP arrivals", "Privacy-sensitive spaces"],
         ["Does not infer gender identity from appearance", "Does not replace a human privacy officer"],
         "Inquiry-only with manual delivery after approval"),
        ("gcc-hospital-reception-protocol", "GCC Hospital Reception Protocol", "Healthcare", "GCC",
         "Clinical-grade reception and navigation protocol for robots in GCC hospitals and clinics. Includes patient triage guidance, wayfinding in HIPAA-adjacent environments, prayer room navigation, and family waiting area management.",
         2200.0, "1.0.0", "medium",
         ["Moxi (Diligent Robotics)", "Aethon TUG", "ROS2-compatible mobile platforms"],
         ["hospital_behaviors.yaml", "wayfinding_maps/", "triage_script_library/", "README.md"],
         ["Hospital reception", "Patient intake direction", "Department wayfinding"],
         ["No diagnosis or treatment advice", "Requires on-site supervision for emergency escalation"],
         "Inquiry-only with manual delivery after approval"),
        ("gcc-retail-floor-assistance-protocol", "GCC Retail Floor Assistance Protocol", "Retail", "GCC",
         "Smart retail assistance protocol for robots on UAE and KSA mall floors. Covers product location assistance, multilingual greeting (Arabic/English/Hindi), modesty-aware behavior near prayer times, and seasonal campaign integration.",
         1800.0, "1.0.0", "low",
         ["Softbank Pepper", "LG CLOi", "Any mobile service robot"],
         ["retail_behaviors.yaml", "product_catalog_integration/", "multilingual_greetings/", "README.md"],
         ["Mall floor guidance", "Product location assistance", "Retail greeting support"],
         ["No checkout/payment processing", "Needs operator escalation path for sensitive incidents"],
         "Inquiry-only with manual delivery after approval"),
    ]
    for slug, name, cat, region, desc, price, ver, risk, hw, files, use_cases, limitations, support_mode in products:
        cur.execute("""INSERT INTO protocol_products (
                        slug, name, category, region, description, price_aed, version, risk_level,
                        hardware_requirements_json, included_files_json, use_cases_json, limitations_json, support_mode, created_at
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (slug, name, cat, region, desc, price, ver, risk,
                     json.dumps(hw), json.dumps(files), json.dumps(use_cases), json.dumps(limitations),
                     support_mode, datetime.utcnow().isoformat()))
    conn.commit()

def create_client(name, email, plan, initial_credits, api_key=None):
    api_key = api_key or f"rm_{secrets.token_urlsafe(24)}"
    conn = _connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO api_clients (name, email, api_key_hash, plan, credits_total, credits_used, is_active, created_at) VALUES (?,?,?,?,?,0,1,?)",
                (name, email, hash_api_key(api_key), plan, initial_credits, datetime.utcnow().isoformat()))
    client_id = cur.lastrowid
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
        create_client(settings.DEMO_CLIENT_NAME, settings.DEMO_CLIENT_EMAIL, "free", 0, api_key=settings.DEMO_API_KEY)
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
    conn.commit()
    cur.execute("SELECT * FROM api_clients WHERE id = ?", (client_id,))
    row = cur.fetchone()
    conn.close()
    return row_to_public(row) if row else None

def list_products(active_only=True):
    conn = _connect()
    cur = conn.cursor()
    q = "SELECT * FROM protocol_products WHERE status = 'active' ORDER BY id" if active_only else "SELECT * FROM protocol_products ORDER BY id"
    cur.execute(q)
    rows = cur.fetchall()
    conn.close()
    return [_product_row(r) for r in rows]

def get_product(product_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM protocol_products WHERE id = ?", (product_id,))
    row = cur.fetchone()
    conn.close()
    return _product_row(row) if row else None

def _product_row(row):
    return {"id": row["id"], "slug": row["slug"], "name": row["name"], "category": row["category"],
            "region": row["region"], "description": row["description"], "price_aed": row["price_aed"],
            "status": row["status"], "version": row["version"], "risk_level": row["risk_level"],
            "hardware_requirements": json.loads(row["hardware_requirements_json"] or "[]"),
            "included_files": json.loads(row["included_files_json"] or "[]"),
            "use_cases": json.loads(row["use_cases_json"] or "[]"),
            "limitations": json.loads(row["limitations_json"] or "[]"),
            "support_mode": row["support_mode"],
            "delivery_type": row["delivery_type"]}

def create_product(slug, name, category, region, description, price_aed, version, risk_level, hardware_requirements, included_files, delivery_type, use_cases=None, limitations=None, support_mode="inquiry_and_manual_fulfillment"):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""INSERT INTO protocol_products (
                    slug, name, category, region, description, price_aed, version, risk_level,
                    hardware_requirements_json, included_files_json, delivery_type, use_cases_json,
                    limitations_json, support_mode, created_at
                ) VALUES (:slug,:name,:category,:region,:description,:price_aed,:version,:risk_level,
                          :hardware_requirements_json,:included_files_json,:delivery_type,:use_cases_json,
                          :limitations_json,:support_mode,:created_at)""",
                {
                    "slug": slug,
                    "name": name,
                    "category": category,
                    "region": region,
                    "description": description,
                    "price_aed": price_aed,
                    "version": version,
                    "risk_level": risk_level,
                    "hardware_requirements_json": json.dumps(hardware_requirements),
                    "included_files_json": json.dumps(included_files),
                    "delivery_type": delivery_type,
                    "use_cases_json": json.dumps(use_cases or []),
                    "limitations_json": json.dumps(limitations or []),
                    "support_mode": support_mode,
                    "created_at": datetime.utcnow().isoformat(),
                })
    conn.commit()
    product_id = cur.lastrowid
    conn.close()
    return get_product(product_id)

def submit_inquiry(product_id, buyer_name, buyer_email, buyer_organization, message, deployment_context):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO protocol_inquiries (product_id, buyer_name, buyer_email, buyer_organization, message, deployment_context, created_at) VALUES (?,?,?,?,?,?,?)",
                (product_id, buyer_name, buyer_email, buyer_organization, message, deployment_context, datetime.utcnow().isoformat()))
    conn.commit()
    inquiry_id = cur.lastrowid
    conn.close()
    return inquiry_id

def get_inquiry(inquiry_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""SELECT i.*, p.name as product_name FROM protocol_inquiries i
                   JOIN protocol_products p ON i.product_id = p.id WHERE i.id = ?""", (inquiry_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def list_inquiries(status=None):
    conn = _connect()
    cur = conn.cursor()
    if status:
        cur.execute("""SELECT i.*, p.name as product_name FROM protocol_inquiries i
                       JOIN protocol_products p ON i.product_id = p.id WHERE i.status = ? ORDER BY i.id DESC""", (status,))
    else:
        cur.execute("""SELECT i.*, p.name as product_name FROM protocol_inquiries i
                       JOIN protocol_products p ON i.product_id = p.id ORDER BY i.id DESC""")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def approve_inquiry(inquiry_id, delivery_notes=None):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM protocol_inquiries WHERE id = ?", (inquiry_id,))
    inquiry = cur.fetchone()
    if not inquiry:
        conn.close()
        return None
    cur.execute("UPDATE protocol_inquiries SET status = 'approved' WHERE id = ?", (inquiry_id,))
    cur.execute("INSERT INTO protocol_entitlements (product_id, inquiry_id, buyer_email, granted_at, status, delivery_notes) VALUES (?,?,?,?,?,?)",
                (inquiry["product_id"], inquiry_id, inquiry["buyer_email"], datetime.utcnow().isoformat(), "active", delivery_notes))
    entitlement_id = cur.lastrowid
    # Record the order
    cur.execute("SELECT price_aed FROM protocol_products WHERE id = ?", (inquiry["product_id"],))
    price_row = cur.fetchone()
    amount_aed = price_row["price_aed"] if price_row else 0.0
    cur.execute("INSERT INTO protocol_orders (inquiry_id, product_id, buyer_email, amount_aed, status, created_at) VALUES (?,?,?,?,?,?)",
                (inquiry_id, inquiry["product_id"], inquiry["buyer_email"], amount_aed, "approved", datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return entitlement_id

def get_entitlements_by_email(buyer_email):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""SELECT e.id, e.product_id, p.name as product_name, e.buyer_email,
                          e.granted_at, e.expires_at, e.status
                   FROM protocol_entitlements e JOIN protocol_products p ON e.product_id = p.id
                   WHERE e.buyer_email = ? ORDER BY e.id DESC""", (buyer_email,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_entitlement_by_id(entitlement_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""SELECT e.*, p.name as product_name, p.slug as product_slug
                   FROM protocol_entitlements e JOIN protocol_products p ON e.product_id = p.id
                   WHERE e.id = ?""", (entitlement_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_product(product_id, **kwargs):
    allowed = {"name", "description", "price_aed", "status", "version", "risk_level",
                "hardware_requirements", "included_files", "use_cases", "limitations", "support_mode"}
    conn = _connect()
    cur = conn.cursor()
    for key, value in kwargs.items():
        if key not in allowed:
            continue
        if key in ("hardware_requirements", "included_files", "use_cases", "limitations"):
            cur.execute(f"UPDATE protocol_products SET {key}_json = ? WHERE id = ?",
                        (json.dumps(value), product_id))
        else:
            cur.execute(f"UPDATE protocol_products SET {key} = ? WHERE id = ?",
                        (value, product_id))
    conn.commit()
    conn.close()
    return get_product(product_id)
