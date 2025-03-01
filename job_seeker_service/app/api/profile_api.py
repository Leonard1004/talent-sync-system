from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import logging
from typing import Dict, Any

from app.database import get_db
from app.api.schemas import ProfileChangeNotification
from app.models.profile import CVProfile, ProfileChangeLog
from app.services.matching_service import sync_profile_to_matching_partner

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/profiles/changes", status_code=202)
async def notify_profile_change(
    notification: ProfileChangeNotification,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    API endpoint that is called when a Job Seeker profile is created, updated, or deleted.
    This triggers synchronization with the matching partner.
    """
    try:
        # Log the change
        log_entry = ProfileChangeLog(
            cv_id=notification.cvId,
            operation=notification.operation,
            synced_to_matching_partner=False,
            payload=notification.profile if notification.profile else None
        )
        db.add(log_entry)
        db.commit()
        
        # Trigger sync to matching partner in background
        background_tasks.add_task(
            sync_profile_to_matching_partner, 
            profile_id=notification.cvId, 
            operation=notification.operation,
            db=db
        )
        
        return {"message": f"Profile change notification received and processing started for {notification.cvId}"}
    except Exception as e:
        logger.error(f"Error processing profile change notification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing change notification: {str(e)}")