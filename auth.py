import os
from datetime import datetime, timedelta
# pyrefly: ignore [missing-import]
from passlib.context import CryptContext
# pyrefly: ignore [missing-import]
from jose import jwt

# We use bcrypt to hash passwords securely
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key for JWT (in production, you would hide this in a .env file)
SECRET_KEY = "your-secret-key-min-32-chars"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# 1. Takes "mypassword" and turns it into "$2b$12$..."
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 2. Checks if the typed password matches the scrambled one in the database
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 3. Creates the digital ID badge (JWT token) that expires in 60 minutes
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
