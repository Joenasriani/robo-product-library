import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src import settings, db, billing
from src.models.schemas import Tender, HealthResponse, ProvidersResponse, AdminCreateClientRequest, AdminCreateClientResponse, CreditTopupRequest, AccountResponse, BillingCheckoutRequest, BillingCheckoutResponse, ApiClientPublic
from src.analyzer import analyze_tender
from src.llm_factory import get_available_providers
from src.auth import require_client, require_admin
from src.pdf_extract import extract_text_from_pdf_bytes

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

app = FastAPI(title="Tender Analyzer GCC", version=settings.APP_VERSION, lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

frontend_dir = Path("frontend")
app.mount("/assets", StaticFiles(directory=str(frontend_dir)), name="assets")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error. Please try again later."})

@app.get("/", include_in_schema=False)
async def dashboard():
    return FileResponse(frontend_dir / "index.html")

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy", service="tender-analyzer-gcc", version=settings.APP_VERSION)

@app.get("/api/v1/providers", response_model=ProvidersResponse)
async def providers(client=Depends(require_client)):
    return ProvidersResponse(available_providers=await get_available_providers(), current_provider=app.state.current_provider, current_model=app.state.current_model)

@app.get("/api/v1/account/me", response_model=AccountResponse)
async def account_me(client=Depends(require_client)):
    row = db.get_client_by_id(client["id"])
    return AccountResponse(client=ApiClientPublic(**db.row_to_public(row)))

@app.post("/api/v1/tenders/analyze")
@limiter.limit("10/minute")
async def analyze(request: Request, tender: Tender, client=Depends(require_client)):
    updated = db.deduct_credit(client["id"], 1)
    result = await analyze_tender(tender)
    payload = result.dict()
    payload["credits_remaining"] = updated["credits_remaining"]
    return [payload]

@app.post("/api/v1/tenders/analyze-file")
@limiter.limit("10/minute")
async def analyze_file(request: Request, file: UploadFile = File(...), title: str = Form(""), issuer: str = Form(""), country: str = Form("GCC"), sector: str = Form(""), client=Depends(require_client)):
    if file.content_type not in {"application/pdf", "text/plain"}:
        raise HTTPException(status_code=400, detail="Only PDF and TXT uploads are supported")
    _MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    content = await file.read(_MAX_BYTES + 1)
    if len(content) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Maximum upload size is 10 MB")
    extracted = extract_text_from_pdf_bytes(content) if file.content_type == "application/pdf" else content.decode("utf-8", errors="ignore")
    if not extracted.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the uploaded file")
    tender = Tender(
        id=f"upload-{client['id']}-{abs(hash(file.filename)) % 1000000}",
        title=title or file.filename,
        description=extracted[:12000],
        issuer=issuer or "Unknown issuer",
        country=country,
        sector=sector or None,
    )
    updated = db.deduct_credit(client["id"], 1)
    result = await analyze_tender(tender)
    payload = result.dict()
    payload["credits_remaining"] = updated["credits_remaining"]
    payload["extracted_characters"] = len(extracted)
    return [payload]

@app.get("/api/v1/admin/clients")
async def admin_list_clients(admin=Depends(require_admin)):
    return db.list_clients()

@app.post("/api/v1/admin/clients", response_model=AdminCreateClientResponse)
async def admin_create_client(payload: AdminCreateClientRequest, admin=Depends(require_admin)):
    client, api_key = db.create_client(payload.name, payload.email, payload.plan, payload.initial_credits)
    return AdminCreateClientResponse(client=ApiClientPublic(**client), api_key=api_key)

@app.post("/api/v1/admin/credits/add")
async def admin_add_credits(payload: CreditTopupRequest, admin=Depends(require_admin)):
    updated = db.add_credits(payload.client_id, payload.credits, payload.reason)
    if not updated:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"client": updated}

@app.post("/api/v1/billing/create-checkout-session", response_model=BillingCheckoutResponse)
async def create_checkout(payload: BillingCheckoutRequest, admin=Depends(require_admin)):
    return BillingCheckoutResponse(**billing.create_checkout_session(payload.client_id, payload.plan, payload.success_url, payload.cancel_url))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.PORT, reload=False, workers=settings.WORKERS)
