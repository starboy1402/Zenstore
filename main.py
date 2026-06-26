# pyrefly: ignore [missing-import]
from fastapi import FastAPI
import models
from database import engine
from routers import auth_router, product_router

# This tells SQLAlchemy to create the database tables if they don't exist yet
models.Base.metadata.create_all(bind=engine)

# This creates the actual FastAPI application instance
app = FastAPI(title="ZenStore AI")

# Register our routers so FastAPI knows they exist
app.include_router(auth_router.router)
app.include_router(product_router.router)

# This is our first endpoint. When someone goes to http://127.0.0.1:8000/, this runs.
@app.get("/")
def read_root():
    return {"message": "Welcome to ZenStore AI API"}
