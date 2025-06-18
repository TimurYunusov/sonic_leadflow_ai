from fastapi import FastAPI
from .routes import router as lead_router

# Initialize the FastAPI app
app = FastAPI()

# Include the router
app.include_router(lead_router)

# Define a root endpoint for testing
@app.get("/")
async def root():
    return {"message": "Welcome to the LeadFlow API"} 