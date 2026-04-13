from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from typing import Literal

class ContentRequest(BaseModel):
    brand_name: str = Field(..., max_length=200)
    brand_context: str = Field(..., max_length=2000)
    campaign_topic: str = Field(..., max_length=500)
    platforms: List[str] = Field(default_factory=lambda: ["LinkedIn", "Instagram"])
    posting_frequency: Optional[str] = "3x per week"
    content_pillars: Optional[List[str]] = None
    region: Optional[str] = "UAE"
    language: Optional[str] = "English"

class PostConcept(BaseModel):
    platform: str
    post_type: str
    caption: str
    hashtags: List[str]
    best_time: str

class ContentCalendarEntry(BaseModel):
    day: str
    platform: str
    topic: str
    format: str

class ContentResult(BaseModel):
    content_calendar: List[ContentCalendarEntry]
    post_concepts: List[PostConcept]
    repurposing_plan: str
    content_themes: List[str]
    confidence_score: float = Field(..., ge=0, le=1)

class ContentAnalysisResult(BaseModel):
    id: str
    result: ContentResult
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
