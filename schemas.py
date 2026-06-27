# pyrefly: ignore [missing-import]
from pydantic import BaseModel, EmailStr
from typing import Optional

#BaseModel is used here to define the structure of data that comes in and goes out of the API
#BaseModel in python is a schema for data validation and serialization


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
    image_path: Optional[str] = None
    image_metadata: Optional[dict] = None
    status: str

    class Config:
        from_attributes = True

#config class here is used for configuring the model to allow it to read data from any source that has a __dict__ attribute
#because without config class it will not be able to read the data from the database
#which is exactly what we need because our models are in the database and we need to return them as response
