import os
from dotenv import load_dotenv

load_dotenv()

APP_VERSION = "1.0.0"
APP_NAME = "Claw Hub Installer Agent"
DB_PATH = os.getenv("DB_PATH", "data/claw_hub_installer.db")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
PORT = int(os.getenv("PORT", "8006"))
WORKERS = int(os.getenv("WORKERS", "1"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
DEMO_CLIENT_NAME = os.getenv("DEMO_CLIENT_NAME", "RoboMarket Demo")
DEMO_CLIENT_EMAIL = os.getenv("DEMO_CLIENT_EMAIL", "demo@robomarket.ae")
DEMO_API_KEY = os.getenv("DEMO_API_KEY", "")
