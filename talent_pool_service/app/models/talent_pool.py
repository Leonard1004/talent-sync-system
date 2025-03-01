import uuid
from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.database import Base

class TalentPool(Base):
    __tablename__ = "talent_pools"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    talent_pool_id = Column(String, unique=True, index=True)
    talent_pool_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SyncJob(Base):
    __tablename__ = "sync_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data = Column(JSON)
    status = Column(String, default="pending")  # pending, success, failed
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_message = Column(String, nullable=True)