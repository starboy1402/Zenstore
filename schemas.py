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

# --- PRODUCT SCHEMAS ---

# What we expect the user to send when creating a product
class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int
    raw_description: Optional[str] = None

# What we send back to the user when they request their products
class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    raw_description: Optional[str]
    ai_description: Optional[str]
    category: Optional[str]
    status: str

    class Config:
        from_attributes = True
