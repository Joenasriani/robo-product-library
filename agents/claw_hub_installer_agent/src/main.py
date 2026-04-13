import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src import settings, db
from src.models.schemas import InstallRequest, InstallAnalysisResult, HealthResponse, ApiClientPublic, AccountResponse, AdminCreateClientRequest, AdminCreateClientResponse, CreditTopupRequest
from src.analyzer import run_analysis
from src.auth import require_client, require_admin

Path("data").mkdir(exist_ok=True)
db.init_db()
db.seed_demo_client()

logging.basicConfig(level=settings.LOG_LEVEL.upper(), format="%(asctime)s %(levelname)-8s %(name)s %(message)s")
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.current_provider = settings.LLM_PROVIDER
    app.state.current_model = settings.LLM_MODEL
    yield

app = FastAPI(title="Claw Hub Installer Agent", version=settings.APP_VERSION, lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

frontend_dir = Path("frontend")
app.mount("/assets", StaticFiles(directory=str(frontend_dir)), name="assets")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error."})

@app.get("/", include_in_schema=False)
async def dashboard():
    return FileResponse(frontend_dir / "index.html")

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy", service="claw-hub-installer-agent", version=settings.APP_VERSION)

@app.get("/api/v1/account/me", response_model=AccountResponse)
async def account_me(client=Depends(require_client)):
    row = db.get_client_by_id(client["id"])
    return AccountResponse(client=ApiClientPublic(**db.row_to_public(row)))

@app.post("/api/v1/install/analyze")
@limiter.limit("10/minute")
async def analyze(request: Request, payload: InstallRequest, client=Depends(require_client)):
    try:
        updated = db.deduct_credit(client["id"], 1)
    except ValueError:
        raise HTTPException(status_code=402, detail="Insufficient credits")
    try:
        result = await run_analysis(payload)
    except ValueError:
        raise HTTPException(status_code=503, detail="No LLM provider configured.")
    except Exception as exc:
        logger.error("LLM failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail="LLM analysis failed.")
    db.save_analysis(client["id"], result.id, f"{payload.package_name} on {payload.target_platform}", result.dict())
    out = result.dict()
    out["credits_remaining"] = updated["credits_remaining"]
    return out

@app.get("/api/v1/install/history")
async def get_history(client=Depends(require_client)):
    return db.get_history(client["id"])

@app.get("/api/v1/admin/clients")
async def admin_list_clients(admin=Depends(require_admin)):
    return db.list_clients()

@app.post("/api/v1/admin/clients", response_model=AdminCreateClientResponse)
async def admin_create_client(body: AdminCreateClientRequest, admin=Depends(require_admin)):
    client, api_key = db.create_client(body.name, body.email, body.plan, body.initial_credits)
    return AdminCreateClientResponse(client=ApiClientPublic(**client), api_key=api_key)

@app.post("/api/v1/admin/credits/add")
async def admin_add_credits(body: CreditTopupRequest, admin=Depends(require_admin)):
    updated = db.add_credits(body.client_id, body.credits, body.reason)
    if not updated:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"client": updated}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.PORT, reload=False, workers=settings.WORKERS)
