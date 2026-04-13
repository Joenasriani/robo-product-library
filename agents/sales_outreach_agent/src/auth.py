from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from src import settings, db

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
_admin_header = APIKeyHeader(name="X-Admin-Token", auto_error=False)

async def require_client(api_key: str = Security(_api_key_header)):
    if not api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing X-API-Key")
    row = db.get_client_by_api_key(api_key)
    if not row or not row["is_active"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or inactive API key")
    return db.row_to_public(row)

async def require_admin(admin_token: str = Security(_admin_header)):
    if not settings.ADMIN_TOKEN:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Admin token not configured")
    if admin_token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin token")
    return {"role": "admin"}
