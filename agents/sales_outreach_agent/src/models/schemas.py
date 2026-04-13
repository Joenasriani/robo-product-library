from typing import List, Literal, Optional
from pydantic import BaseModel, Field, EmailStr

class OutreachRequest(BaseModel):
    company_name: str = Field(..., max_length=200)
    target_role: str = Field(..., max_length=200)
    problem_statement: str = Field(..., max_length=2000)
    service_offer: str = Field(..., max_length=1000)
    region: Optional[str] = "GCC"
    tone: Optional[Literal["formal", "friendly", "direct"]] = "formal"

class OutreachResult(BaseModel):
    short_message: str
    followup_message: str
    call_to_action: str
    value_proposition: str
    subject_line: str
    confidence_score: float = Field(..., ge=0, le=1)

class OutreachAnalysisResult(BaseModel):
    id: str
    result: OutreachResult
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
