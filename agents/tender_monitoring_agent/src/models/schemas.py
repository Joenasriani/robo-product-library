from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from typing import Literal

class MonitoringRequest(BaseModel):
    target_sectors: List[str] = Field(..., min_items=1)
    countries: List[str] = Field(default_factory=lambda: ["UAE", "Saudi Arabia"])
    keywords: List[str] = Field(..., min_items=1)
    company_profile: str = Field(..., max_length=2000)
    budget_range: Optional[str] = None
    exclusion_keywords: Optional[List[str]] = None

class TenderOpportunity(BaseModel):
    title: str
    estimated_value: Optional[str] = None
    country: str
    sector: str
    match_score: int = Field(..., ge=0, le=100)
    match_rationale: str
    recommended_action: str
    source_type: str
    source_url: Optional[str] = None

class MonitoringResult(BaseModel):
    matched_opportunities: List[TenderOpportunity]
    monitoring_summary: str
    top_opportunity_rationale: str
    shortlist_count: int
    next_recommended_action: str
    confidence_score: float = Field(..., ge=0, le=1)
    ai_generated: bool = True
    disclaimer: str = "Results are AI-generated research summaries based on your criteria. Always verify opportunities against official procurement portals before taking action."

class MonitoringAnalysisResult(BaseModel):
    id: str
    result: MonitoringResult
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
