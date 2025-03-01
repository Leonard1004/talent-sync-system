from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class TalentPoolBase(BaseModel):
    talent_pool_id: str
    talent_pool_name: str

class TalentPoolCreate(TalentPoolBase):
    pass

class TalentPool(TalentPoolBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class SyncJobBase(BaseModel):
    data: dict
    status: str = "pending"
    retry_count: int = 0
    error_message: Optional[str] = None

class SyncJobCreate(SyncJobBase):
    pass

class SyncJob(SyncJobBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True