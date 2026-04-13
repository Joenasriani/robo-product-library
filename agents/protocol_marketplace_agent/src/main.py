import io
import logging
import zipfile
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from src import settings, db
from src.models.schemas import (InquiryRequest, AdminApproveInquiryRequest, AdminCreateProtocolRequest,
    AdminUpdateProtocolRequest,
    HealthResponse, ApiClientPublic, AccountResponse, AdminCreateClientRequest, AdminCreateClientResponse)
from src.auth import require_client, require_admin

Path("data").mkdir(exist_ok=True)
db.init_db()
db.seed_demo_client()

logging.basicConfig(level=settings.LOG_LEVEL.upper(), format="%(asctime)s %(levelname)-8s %(name)s %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="Protocol Marketplace", version=settings.APP_VERSION, lifespan=lifespan)
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
    return HealthResponse(status="healthy", service="protocol-marketplace-agent", version=settings.APP_VERSION)

@app.get("/api/v1/account/me", response_model=AccountResponse)
async def account_me(client=Depends(require_client)):
    row = db.get_client_by_id(client["id"])
    return AccountResponse(client=ApiClientPublic(**db.row_to_public(row)))

@app.get("/api/v1/products")
async def list_products():
    return db.list_products(active_only=True)

@app.get("/api/v1/products/{product_id}")
async def get_product(product_id: int):
    p = db.get_product(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p

@app.post("/api/v1/inquiries")
async def submit_inquiry(body: InquiryRequest):
    p = db.get_product(body.product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    inquiry_id = db.submit_inquiry(body.product_id, body.buyer_name, str(body.buyer_email),
                                    body.buyer_organization, body.message, body.deployment_context)
    return {"inquiry_id": inquiry_id, "status": "pending", "message": "Your inquiry has been submitted. We will review and respond within 1 business day."}

@app.get("/api/v1/my-entitlements")
async def my_entitlements(email: str = Query(..., description="Buyer email address")):
    return db.get_entitlements_by_email(email)


@app.get("/api/v1/my-entitlements/{entitlement_id}/download")
async def download_entitlement(entitlement_id: int, email: str = Query(..., description="Buyer email for verification")):
    entitlement = db.get_entitlement_by_id(entitlement_id)
    if not entitlement:
        raise HTTPException(status_code=404, detail="Entitlement not found")
    if entitlement["buyer_email"].lower() != email.lower():
        raise HTTPException(status_code=403, detail="Email does not match entitlement record")
    if entitlement["status"] != "active":
        raise HTTPException(status_code=403, detail="Entitlement is not active")

    slug = entitlement["product_slug"]
    protocol_dir = Path("data/protocols") / slug

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        if protocol_dir.exists():
            for file_path in sorted(protocol_dir.rglob("*")):
                if file_path.is_file():
                    arcname = file_path.relative_to(protocol_dir)
                    zf.write(file_path, arcname)
        else:
            # Fallback: generate a README from DB product record
            product = db.get_product(entitlement["product_id"])
            if product:
                lines = [
                    f"# {product['name']}",
                    f"Version: {product['version']}",
                    f"Region: {product['region']}",
                    f"Risk Level: {product['risk_level']}",
                    "",
                    product.get("description", ""),
                    "",
                    "## Included Files",
                ]
                for f_name in product.get("included_files", []):
                    lines.append(f"- {f_name}")
                lines += ["", "## Support", "protocols@robomarket.ae"]
                zf.writestr("README.md", "\n".join(lines))

    buf.seek(0)
    filename = f"{slug}-v{entitlement.get('product_name', slug)}.zip".replace(" ", "_")
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{slug}.zip"'},
    )

@app.post("/api/v1/admin/inquiries/{inquiry_id}/approve")
async def approve_inquiry(inquiry_id: int, body: AdminApproveInquiryRequest, admin=Depends(require_admin)):
    entitlement_id = db.approve_inquiry(inquiry_id, body.delivery_notes)
    if entitlement_id is None:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    return {"entitlement_id": entitlement_id, "inquiry_id": inquiry_id, "status": "approved"}

@app.get("/api/v1/admin/inquiries")
async def list_inquiries(status: str = Query(None), admin=Depends(require_admin)):
    return db.list_inquiries(status=status)

@app.get("/api/v1/admin/products")
async def admin_list_products(admin=Depends(require_admin)):
    return db.list_products(active_only=False)

@app.post("/api/v1/admin/products")
async def admin_create_product(body: AdminCreateProtocolRequest, admin=Depends(require_admin)):
    return db.create_product(body.slug, body.name, body.category, body.region, body.description,
                              body.price_aed, body.version, body.risk_level, body.hardware_requirements,
                              body.included_files, body.delivery_type)


@app.patch("/api/v1/admin/products/{product_id}")
async def admin_update_product(product_id: int, body: AdminUpdateProtocolRequest, admin=Depends(require_admin)):
    updated = db.update_product(
        product_id,
        **{k: v for k, v in body.dict().items() if v is not None},
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

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
