
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./zenstore.db"

# connect_args={"check_same_thread": False} is needed only for SQLite in FastAPI
# engine here is used to connect to the database
# sessionlocal is used to create a session to interact with the database
# base here is used to create a base class for all our models
# check same thread is used to check the same thread for sqlite 
# it helps to run multiple requests at the same time

# autocommit=False means that we need to commit the changes manually
# autoflush=False means that we need to flush the changes manually

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All our models will inherit from this Base class
Base = declarative_base()
