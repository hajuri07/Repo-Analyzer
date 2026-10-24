from pydantic import BaseModel,Field,EmailStr, HttpUrl
from datetime import datetime
from typing import Literal
from pydantic import field_validator


class UserCreate(BaseModel):
    username: str = Field(...,min_length= 3,max_length= 12)
    email : EmailStr
    password :str = Field(...,min_length = 8 , description="Password must be at least 8 characters long ")

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class UserResponse(BaseModel):
    id :int
    username : str
    email : EmailStr
    created_at : datetime

    class Config:
        from_attributes = True
class SubmissionCreate(BaseModel):
    repo_url: HttpUrl

class SubmissionResponse(BaseModel):
    id: int
    user_id: int
    repo_url: HttpUrl
    submitted_at: datetime
    status: str  # PENDING / PROCESSING / COMPLETED / FAILED
    error_message: str | None = None

    class Config:
        from_attributes = True
    id: int
    user_id: int
    repo_url: HttpUrl
    submitted_at: datetime

    class Config:
        from_attributes = True
class Finding(BaseModel):
    severity: Literal["critical", "high", "medium", "low"] = "medium"
    title: str = Field(..., min_length=3, max_length=140)
    detail: str = Field(..., min_length=3, max_length=900)
    area: str = Field(default="Codebase", max_length=100)
    file: str | None = Field(default=None, max_length=300)
    line_hint: int | None = Field(default=None, ge=1)
    excerpt: str | None = Field(default=None, max_length=500)


class Recommendation(BaseModel):
    title: str = Field(..., min_length=3, max_length=140)
    detail: str = Field(..., min_length=3, max_length=900)
    impact: Literal["high", "medium", "low"] = "medium"


class HealthMetric(BaseModel):
    name: str = Field(..., min_length=3, max_length=60)
    score: float = Field(..., ge=0, le=10)
    rationale: str = Field(..., min_length=3, max_length=300)


class RoadmapItem(BaseModel):
    priority: Literal["now", "next", "later"]
    title: str = Field(..., min_length=3, max_length=140)
    detail: str = Field(..., min_length=3, max_length=900)
    effort: Literal["15 min", "1 hour", "half day", "1+ days"]


class ReviewResponse(BaseModel):
    overall_score: float = Field(..., ge=0, le=10)
    summary: str = Field(..., min_length=3, max_length=3000)
    issues: list[Finding]
    suggestions: list[Recommendation]
    metrics: list[HealthMetric] = []
    roadmap: list[RoadmapItem] = []

    @field_validator("issues", mode="before")
    @classmethod
    def support_legacy_issue_rows(cls, value):
        return [item if isinstance(item, dict) else {"title": "Review finding", "detail": str(item)} for item in (value or [])]

    @field_validator("suggestions", mode="before")
    @classmethod
    def support_legacy_suggestion_rows(cls, value):
        return [item if isinstance(item, dict) else {"title": "Recommended next step", "detail": str(item)} for item in (value or [])]

    @field_validator("metrics", "roadmap", mode="before")
    @classmethod
    def default_missing_collections(cls, value):
        return value or []

class Token(BaseModel):
    access_token : str
    token_type: str
    
class TokenData(BaseModel):
    user_id: int | None = None
