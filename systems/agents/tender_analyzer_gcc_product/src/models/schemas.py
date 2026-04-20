from typing import List, Literal, Optional
from pydantic import BaseModel, Field, EmailStr

class Tender(BaseModel):
    id: str = Field(..., max_length=100)
    title: str = Field(..., max_length=500)
    description: str = Field(..., max_length=12000)
    issuer: str = Field(..., max_length=300)
    country: Optional[str] = "GCC"
    sector: Optional[str] = None
    source_url: Optional[str] = None

class Analysis(BaseModel):
    summary: str
    key_requirements: List[str]
    confidence_score: float = Field(..., ge=0, le=1)
    score: int = Field(..., ge=0, le=100)
    recommended_action: Literal["pursue", "review", "skip"]
    risk_level: Literal["low", "medium", "high"]
    reasoning: str

class TenderAnalysisResult(BaseModel):
    id: str
    analysis: Analysis
    credits_remaining: Optional[int] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

class ProvidersResponse(BaseModel):
    available_providers: List[str]
    current_provider: str
    current_model: str

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

class BillingCheckoutRequest(BaseModel):
    client_id: int
    plan: Literal["starter", "growth", "enterprise"] = "starter"
    success_url: str
    cancel_url: str

class BillingCheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str
