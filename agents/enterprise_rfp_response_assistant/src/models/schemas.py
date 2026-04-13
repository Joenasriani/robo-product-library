from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from typing import Literal

class RFPRequest(BaseModel):
    id: str = Field(..., max_length=100)
    rfp_text: str = Field(..., max_length=15000)
    company_capabilities: str = Field(..., max_length=3000)
    company_name: str = Field(..., max_length=200)
    submission_deadline: Optional[str] = None

class RequirementItem(BaseModel):
    requirement: str
    can_meet: bool
    notes: str

class RFPResponseResult(BaseModel):
    requirement_matrix: List[RequirementItem]
    response_outline: List[str]
    executive_summary_draft: str
    technical_approach_draft: str
    risk_flags: List[str]
    win_probability: int = Field(..., ge=0, le=100)
    confidence_score: float = Field(..., ge=0, le=1)

class RFPAnalysisResult(BaseModel):
    id: str
    result: RFPResponseResult
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
