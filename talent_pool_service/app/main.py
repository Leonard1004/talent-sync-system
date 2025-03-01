from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api import talent_pool_api
from app.database import Base, engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Talent Pool Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(talent_pool_api.router, prefix="/api", tags=["talent-pools"])

@app.get("/", tags=["health"])
async def health_check():
    return {"status": "healthy", "service": "talent-pool-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)