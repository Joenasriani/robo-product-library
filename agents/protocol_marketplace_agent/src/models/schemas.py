from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from typing import Literal

class ProtocolProduct(BaseModel):
    id: int
    slug: str
    name: str
    category: str
    region: str
    description: str
    price_aed: float
    status: str
    version: str
    risk_level: str
    hardware_requirements: List[str] = []
    included_files: List[str] = []
    delivery_type: str = "download"

class InquiryRequest(BaseModel):
    product_id: int
    buyer_name: str = Field(..., max_length=200)
    buyer_email: EmailStr
    buyer_organization: str = Field(..., max_length=200)
    message: Optional[str] = Field(None, max_length=2000)
    deployment_context: Optional[str] = None

class InquiryRecord(BaseModel):
    id: int
    product_id: int
    product_name: str
    buyer_name: str
    buyer_email: str
    buyer_organization: str
    message: Optional[str] = None
    status: str
    created_at: str

class EntitlementRecord(BaseModel):
    id: int
    product_id: int
    product_name: str
    buyer_email: str
    granted_at: str
    expires_at: Optional[str] = None
    status: str

class AdminApproveInquiryRequest(BaseModel):
    inquiry_id: int
    delivery_notes: Optional[str] = None

class AdminCreateProtocolRequest(BaseModel):
    slug: str
    name: str
    category: str
    region: str
    description: str
    price_aed: float
    version: str = "1.0.0"
    risk_level: str = "medium"
    hardware_requirements: List[str] = []
    included_files: List[str] = []
    delivery_type: str = "download"

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

class AdminUpdateProtocolRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_aed: Optional[float] = None
    status: Optional[str] = None
    version: Optional[str] = None
    risk_level: Optional[str] = None
    hardware_requirements: Optional[List[str]] = None
    included_files: Optional[List[str]] = None


class AdminCreateClientRequest(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    plan: Literal["starter", "growth", "enterprise"] = "starter"
    initial_credits: int = Field(50, ge=0, le=100000)

class AdminCreateClientResponse(BaseModel):
    client: ApiClientPublic
    api_key: str

class AccountResponse(BaseModel):
    client: ApiClientPublic
