import io
import logging
import zipfile
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src import settings, db
from src.models.schemas import (AgentProduct, EntitlementRecord, AdminGrantEntitlementRequest,
    AdminCreateProductRequest, HealthResponse, ApiClientPublic, AccountResponse,
    AdminCreateClientRequest, AdminCreateClientResponse)
from src.auth import require_client, require_admin

Path("data").mkdir(exist_ok=True)
db.init_db()
db.seed_demo_client()

logging.basicConfig(level=settings.LOG_LEVEL.upper(), format="%(asctime)s %(levelname)-8s %(name)s %(message)s")
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="AI Agent Download Center", version=settings.APP_VERSION, lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

frontend_dir = Path("frontend")
app.mount("/assets", StaticFiles(directory=str(frontend_dir)), name="assets")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})

@app.get("/", include_in_schema=False)
async def dashboard():
    return FileResponse(frontend_dir / "index.html")

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy", service="ai-agent-download-center", version=settings.APP_VERSION)

@app.get("/api/v1/account/me", response_model=AccountResponse)
async def account_me(client=Depends(require_client)):
    row = db.get_client_by_id(client["id"])
    return AccountResponse(client=ApiClientPublic(**db.row_to_public(row)))

@app.get("/api/v1/catalog")
async def list_catalog():
    return db.list_products(active_only=True)

@app.get("/api/v1/catalog/{product_id}")
async def get_product(product_id: int):
    product = db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/api/v1/my-downloads")
async def my_downloads(client=Depends(require_client)):
    return db.get_entitlements(client["id"])

@app.get("/api/v1/download/{product_id}")
async def download_product(product_id: int, client=Depends(require_client)):
    product = db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    entitlement = db.get_entitlement(client["id"], product_id)
    if not entitlement:
        raise HTTPException(status_code=403, detail="No entitlement for this product. Please submit an inquiry to request access.")
    return {
        "entitlement_id": entitlement["id"],
        "product_slug": product["slug"],
        "product_name": product["name"],
        "download_url": f"/api/v1/download/{product_id}/file",
        "expires_in_seconds": 3600,
        "message": "Your download is ready. Click the URL to retrieve the package.",
    }


@app.get("/api/v1/download/{product_id}/file")
@limiter.limit("20/minute")
async def download_product_file(request: Request, product_id: int, client=Depends(require_client)):
    product = db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    entitlement = db.get_entitlement(client["id"], product_id)
    if not entitlement:
        raise HTTPException(status_code=403, detail="No entitlement for this product.")

    agent_dir = Path(settings.AGENTS_ROOT) / product["slug"]
    if not agent_dir.exists() or not any(agent_dir.iterdir()):
        raise HTTPException(
            status_code=503,
            detail=(
                "The deliverable for this agent product is not yet staged for automated download. "
                "Delivery is fulfilled manually after inquiry approval. "
                "Please contact support@robomarket.ae to arrange delivery."
            ),
        )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(agent_dir.rglob("*")):
            if file_path.is_file():
                arcname = file_path.relative_to(agent_dir)
                zf.write(file_path, arcname)

    buf.seek(0)
    filename = f"{product['slug']}-v{product['version']}.zip"
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

@app.post("/api/v1/admin/products")
async def admin_create_product(body: AdminCreateProductRequest, admin=Depends(require_admin)):
    product = db.create_product(body.slug, body.name, body.description, body.version, body.category,
                                 body.price_aed, body.requirements, body.included_files)
    return product

@app.get("/api/v1/admin/products")
async def admin_list_products(admin=Depends(require_admin)):
    return db.list_products(active_only=False)

@app.post("/api/v1/admin/entitlements")
async def admin_grant_entitlement(body: AdminGrantEntitlementRequest, admin=Depends(require_admin)):
    product = db.get_product(body.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    entitlement_id = db.grant_entitlement(body.client_id, body.product_id, body.expires_at)
    return {"entitlement_id": entitlement_id, "client_id": body.client_id, "product_id": body.product_id}

@app.get("/api/v1/admin/entitlements")
async def admin_list_entitlements(admin=Depends(require_admin)):
    return db.list_all_entitlements()

@app.get("/api/v1/admin/clients")
async def admin_list_clients(admin=Depends(require_admin)):
    return db.list_clients()

@app.post("/api/v1/admin/clients", response_model=AdminCreateClientResponse)
async def admin_create_client(body: AdminCreateClientRequest, admin=Depends(require_admin)):
    client, api_key = db.create_client(body.name, body.email, body.plan, body.initial_credits)
    return AdminCreateClientResponse(client=ApiClientPublic(**client), api_key=api_key)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.PORT, reload=False, workers=settings.WORKERS)
