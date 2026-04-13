from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from typing import Literal

class VideoRequest(BaseModel):
    robot_name: str = Field(..., max_length=200)
    robot_type: str = Field(..., max_length=200)
    feature_list: List[str] = Field(..., min_items=1)
    visual_style: Optional[str] = "professional corporate"
    target_duration: Optional[int] = 90
    target_audience: Optional[str] = "enterprise buyers"
    use_case: Optional[str] = None

class Scene(BaseModel):
    scene_number: int
    title: str
    duration_seconds: int
    description: str
    camera_angle: str
    ai_image_prompt: str

class VideoResult(BaseModel):
    storyboard: List[Scene]
    scene_plan_summary: str
    production_notes: str
    voiceover_script: str
    total_estimated_duration: int
    confidence_score: float = Field(..., ge=0, le=1)

class VideoAnalysisResult(BaseModel):
    id: str
    result: VideoResult
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
