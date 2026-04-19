from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from typing import Literal

class LeadResearchRequest(BaseModel):
    company_name: str = Field(..., max_length=200)
    industry: str = Field(..., max_length=200)
    region: Optional[str] = "GCC"
    company_size: Optional[str] = None
    additional_context: Optional[str] = Field(None, max_length=2000)

class OpportunitySignal(BaseModel):
    signal: str
    strength: str

class LeadResearchResult(BaseModel):
    company_summary: str
    opportunity_signals: List[OpportunitySignal]
    qualification_notes: str
    lead_score: int = Field(..., ge=0, le=100)
    lead_status: str
    recommended_approach: str
    confidence_score: float = Field(..., ge=0, le=1)

class LeadResearchAnalysisResult(BaseModel):
    id: str
    result: LeadResearchResult
    credits_remaining: Optional[int] = None

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
