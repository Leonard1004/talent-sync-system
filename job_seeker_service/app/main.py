from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api import bulk_api, profile_api
from app.database import Base, engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Seeker Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bulk_api.router, prefix="/api", tags=["bulk"])
app.include_router(profile_api.router, prefix="/api", tags=["profiles"])

@app.get("/", tags=["health"])
async def health_check():
    return {"status": "healthy", "service": "job-seeker-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)