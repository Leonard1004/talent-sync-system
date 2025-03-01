import requests
import logging
import time
from sqlalchemy.orm import Session
from sqlalchemy import update
import json

from app.config import settings
from app.models.profile import CVProfile, ProfileChangeLog

logger = logging.getLogger(__name__)

def sync_profile_to_matching_partner(profile_id: str, operation: str, db: Session):
    """
    Sync profile changes to the third-party matching partner.
    Implements retry logic and idempotency.
    """
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds
    
    # Get the latest change log entry for this profile
    log_entry = db.query(ProfileChangeLog)\
        .filter(ProfileChangeLog.cv_id == profile_id)\
        .filter(ProfileChangeLog.operation == operation)\
        .filter(ProfileChangeLog.synced_to_matching_partner == False)\
        .order_by(ProfileChangeLog.timestamp.desc())\
        .first()
    
    if not log_entry:
        logger.warning(f"No unsynchronized change log found for profile {profile_id}, operation {operation}")
        return
    
    # If this is a DELETE operation, we only need the profile ID
    if operation == "DELETE":
        payload = {"cvId": profile_id, "operation": "DELETE"}
    else:
        # For INSERT or UPDATE operations, get the full profile data
        profile = db.query(CVProfile).filter(CVProfile.cv_id == profile_id).first()
        if not profile:
            logger.error(f"Profile {profile_id} not found for {operation} operation")
            return
        
        
        payload = {
            "cvId": profile_id,
            "operation": operation,
            "profile": json.loads(log_entry.payload) if log_entry.payload else None
        }
    
    # Add idempotency key to prevent duplicate processing
    idempotency_key = f"{profile_id}_{operation}_{log_entry.id}"
    headers = {
        "Content-Type": "application/json",
        "X-Idempotency-Key": idempotency_key
    }
    
    # Try to send the notification with retries
    success = False
    retries = 0
    last_error = None
    
    while not success and retries < MAX_RETRIES:
        try:
            response = requests.post(
                settings.MATCHING_PARTNER_API_URL,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code in (200, 201, 202, 204):
                success = True
                logger.info(f"Successfully synced profile {profile_id} to matching partner")
            else:
                last_error = f"API returned status code {response.status_code}: {response.text}"
                logger.warning(f"Failed to sync profile {profile_id}: {last_error}")
                retries += 1
                time.sleep(RETRY_DELAY)
        except Exception as e:
            last_error = str(e)
            logger.exception(f"Error syncing profile {profile_id} to matching partner")
            retries += 1
            time.sleep(RETRY_DELAY)
    
    # Update the log entry
    if success:
        log_entry.synced_to_matching_partner = True
        db.commit()
    else:
        logger.error(f"Failed to sync profile {profile_id} after {MAX_RETRIES} retries: {last_error}")