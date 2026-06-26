from fastapi import FastAPI

# This creates the actual FastAPI application instance
app = FastAPI(title="ZenStore AI")

# This is our first endpoint. When someone goes to http://127.0.0.1:8000/, this runs.
@app.get("/")
def read_root():
    return {"message": "Welcome to ZenStore AI API"}
