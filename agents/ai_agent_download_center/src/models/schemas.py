from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Literal

class AgentProduct(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    version: str
    category: str
    price_aed: float
    status: str
    file_size_mb: Optional[float] = None
    requirements: List[str] = []
    included_files: List[str] = []

class EntitlementRecord(BaseModel):
    id: int
    product_id: int
    product_name: str
    granted_at: str
    expires_at: Optional[str] = None
    status: str

class DownloadRecord(BaseModel):
    entitlement_id: int
    product_slug: str
    download_url: str
    expires_in_seconds: int = 3600

class AdminGrantEntitlementRequest(BaseModel):
    client_id: int
    product_id: int
    expires_at: Optional[str] = None

class AdminCreateProductRequest(BaseModel):
    slug: str
    name: str
    description: str
    version: str = "1.0.0"
    category: str
    price_aed: float
    requirements: List[str] = []
    included_files: List[str] = []

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

class ApiClientPublic(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr] = None
    plan: str
    credits_total: int
    credits_used: int
    credits_remaining: int
    is_active: bool

class AdminCreateClientRequest(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    plan: Literal["starter", "growth", "enterprise"] = "starter"
    initial_credits: int = Field(50, ge=0, le=100000)

class AdminCreateClientResponse(BaseModel):
    client: ApiClientPublic
    api_key: str

class CreditTopupRequest(BaseModel):
    client_id: int
    credits: int = Field(..., ge=1, le=100000)
    reason: str = "manual_topup"

class AccountResponse(BaseModel):
    client: ApiClientPublic
