# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
# pyrefly: ignore [missing-import]
from sqlalchemy.sql import func
# pyrefly: ignore [missing-import]
from database import Base



# HERE USER CLASS COME FROM database.py which is imported from Base
# this file is the model of the database where entities are defined
# and their relationships are defined
class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    email         = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name     = Column(String, nullable=False)
    created_at    = Column(DateTime, default=func.now())
    products      = relationship("Product", back_populates="owner")
    # here relationship means one user can have many products
    # back_populates means that the products will have a back_populates to the owner
    # owner_id is the foreign key of the products table
    # nullable=False means that the owner_id cannot be null
    

class Product(Base):
    __tablename__ = "products"
    id              = Column(Integer, primary_key=True, index=True)
    owner_id        = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name            = Column(String, nullable=False)
    price           = Column(Float, nullable=False)
    stock           = Column(Integer, nullable=False, default=0)
    raw_description = Column(Text, nullable=True)
    ai_description  = Column(Text, nullable=True)
    category        = Column(String, nullable=True)
    image_path      = Column(String, nullable=True)
    image_metadata  = Column(JSON, nullable=True)
    status          = Column(String, nullable=False, default="pending")
    created_at      = Column(DateTime, default=func.now())
    updated_at      = Column(DateTime, default=func.now(), onupdate=func.now())
    owner           = relationship("User", back_populates="products")

class BatchJob(Base):
    __tablename__ = "batch_jobs"
    id          = Column(Integer, primary_key=True, index=True)
    owner_id    = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename    = Column(String, nullable=False)
    total       = Column(Integer, nullable=False, default=0)
    processed   = Column(Integer, nullable=False, default=0)
    failed      = Column(Integer, nullable=False, default=0)
    failed_rows = Column(JSON, nullable=True)
    status      = Column(String, nullable=False, default="queued")
    created_at  = Column(DateTime, default=func.now())
