from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from typing import Literal

class InstallRequest(BaseModel):
    target_platform: str = Field(..., max_length=200)
    package_name: str = Field(..., max_length=200)
    package_version: Optional[str] = None
    os_version: Optional[str] = None
    environment_type: Optional[str] = "production"
    constraints: Optional[str] = Field(None, max_length=1000)

class InstallStep(BaseModel):
    step_number: int
    title: str
    command: Optional[str] = None
    description: str
    notes: Optional[str] = None

class CompatibilityNote(BaseModel):
    component: str
    status: str
    details: str

class InstallResult(BaseModel):
    install_steps: List[InstallStep]
    compatibility_notes: List[CompatibilityNote]
    troubleshooting_guide: str
    estimated_install_time: str
    prerequisites: List[str]
    confidence_score: float = Field(..., ge=0, le=1)

class InstallAnalysisResult(BaseModel):
    id: str
    result: InstallResult
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
