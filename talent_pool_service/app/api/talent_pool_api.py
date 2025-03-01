from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from typing import List

from app.database import get_db
from app.api.schemas import TalentPoolCreate, TalentPool

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/talent-pools", response_model=List[TalentPool])
async def get_talent_pools(db: Session = Depends(get_db)):
    """Get all talent pools"""
    from app.models.talent_pool import TalentPool as TalentPoolModel
    
    talent_pools = db.query(TalentPoolModel).all()
    return talent_pools

@router.post("/talent-pools", response_model=TalentPool, status_code=201)
async def create_talent_pool(talent_pool: TalentPoolCreate, db: Session = Depends(get_db)):
    """Create a new talent pool"""
    from app.models.talent_pool import TalentPool as TalentPoolModel
    
    # Check if talent pool with this ID already exists
    existing = db.query(TalentPoolModel).filter(
        TalentPoolModel.talent_pool_id == talent_pool.talent_pool_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Talent pool with this ID already exists")
    
    # Create new talent pool
    db_talent_pool = TalentPoolModel(
        talent_pool_id=talent_pool.talent_pool_id,
        talent_pool_name=talent_pool.talent_pool_name
    )
    
    db.add(db_talent_pool)
    db.commit()
    db.refresh(db_talent_pool)
    
    return db_talent_pool

@router.get("/talent-pools/{talent_pool_id}", response_model=TalentPool)
async def get_talent_pool(talent_pool_id: str, db: Session = Depends(get_db)):
    """Get a specific talent pool by ID"""
    from app.models.talent_pool import TalentPool as TalentPoolModel
    
    talent_pool = db.query(TalentPoolModel).filter(
        TalentPoolModel.talent_pool_id == talent_pool_id
    ).first()
    
    if not talent_pool:
        raise HTTPException(status_code=404, detail="Talent pool not found")
    
    return talent_pool

@router.post("/trigger-sync")
async def trigger_sync():
    """
    Manually trigger the sync process (useful for testing)
    """
    from app.tasks.sync_tasks import sync_talent_pool_data
    
    # Start the sync task
    task = sync_talent_pool_data.delay()
    
    return {"message": "Sync task started", "task_id": task.id}