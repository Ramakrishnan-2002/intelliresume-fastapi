from pydantic import BaseModel,EmailStr


class CreateUserModel(BaseModel):
    name :str
    email :EmailStr
    password : str

class TokenResponseData(BaseModel):
    id: int
    email: EmailStr

class Token(BaseModel):
    access_token: str
    refresh_token: str  # Added refresh_token field
    token_type: str 

from typing import Optional

class ResumeDetails(BaseModel):
    jd: str
    name: str
    phone: str
    location: str
    email: EmailStr
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: str
    work: str
    skills: str
    education: str
    projects: str
    certifications: str

    class Config:
        from_attributes=True
