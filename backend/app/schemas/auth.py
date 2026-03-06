from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str             # Needed to create the Patient profile
    email: EmailStr
    phone: str
    password: str
    role: str = "patient" # Defaults to patient for public registration

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    # refresh_token is usually stored in an HTTP-only cookie, 
    # but we will return it here for simplicity in testing.
    refresh_token: str 

class UserResponse(BaseModel):
    id: str
    email: str
    phone: str
    role: str
    linked_id: Optional[str] = None
    
    class Config:
        from_attributes = True