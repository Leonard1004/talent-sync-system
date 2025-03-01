import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
import json

# Setup in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the test database
Base.metadata.create_all(bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_notify_profile_change():
    # Sample profile change notification
    notification = {
        "cvId": "test-cv-id-1",
        "operation": "UPDATE",
        "profile": {
            "user": {
                "userId": "test-user-id",
                "candidateCode": "TEST-001"
            },
            "cvProfile": {
                "workingHours": 40,
                "willingToTravel": True
            }
        }
    }
    
    # Send request to the profile changes API endpoint
    response = client.post("/api/profiles/changes", json=notification)
    
    # Check response
    assert response.status_code == 202
    assert "Profile change notification received" in response.json()["message"]