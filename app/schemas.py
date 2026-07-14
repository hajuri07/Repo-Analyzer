from pydantic import BaseModel,Field,EmailStr
from datetime import datetime
from typing import List
from pydantic import HttpUrl


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
    repo_url :str

class SubmissionResponse(BaseModel):
    id: int
    user_id: int
    repo_url: HttpUrl
    submitted_at: datetime

    class Config:
        from_attributes = True
class ReviewResponse(BaseModel):
    overall_score : float
    summary :str
    issues:List[str]
    suggestions : List[str]

class Token(BaseModel):
    access_token : str
    token_type: str
    
class TokenData(BaseModel):
    user_id: int | None = None