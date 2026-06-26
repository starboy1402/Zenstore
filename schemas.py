# pyrefly: ignore [missing-import]
from pydantic import BaseModel, EmailStr
from typing import Optional

# This is what we expect the user to send us when they register
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

# This is what we send BACK to the user (notice we hide the password!)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str

    class Config:
        from_attributes = True

# This is the format of the JWT token we send back when they log in
class Token(BaseModel):
    access_token: str
    token_type: str
