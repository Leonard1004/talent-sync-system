import requests
import logging
import json
from celery import shared_task
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.config import settings
from app.models.talent_pool import SyncJob, TalentPool

logger = logging.getLogger(__name__)

@shared_task
def sync_talent_pool_data():
    """
    Scheduled background task that pushes talent pool data to the job seeker environment.
    """
    logger.info("Starting talent pool data synchronization")
    
    try:
        db = SessionLocal()
        
        # Fetch all talent pools
        talent_pools = db.query(TalentPool).all()
        
        if not talent_pools:
            logger.info("No talent pools found to sync")
            return {"status": "success", "message": "No talent pools found to sync"}
        
        # Prepare data for bulk API
        profiles_data = []
        
        for talent_pool in talent_pools:
            members_data = get_talent_pool_members(talent_pool.talent_pool_id)
            
            for member_data in members_data:
                # Add talent pool info to each member's profile
                if "memberOf" not in member_data:
                    member_data["memberOf"] = []
                
                member_data["memberOf"].append({
                    "talentPoolId": talent_pool.talent_pool_id,
                    "talentPoolName": talent_pool.talent_pool_name
                })
                
                profiles_data.append(member_data)
        
        # Create a bulk payload
        bulk_payload = {"profiles": profiles_data}
        
        # Create a sync job record
        sync_job = SyncJob(
            data=bulk_payload,
            status="pending"
        )
        db.add(sync_job)
        db.commit()
        
        # Send data to Job Seeker Bulk API
        send_bulk_data_to_job_seeker.delay(sync_job.id)
        
        return {"status": "success", "message": f"Scheduled sync for {len(profiles_data)} profiles"}
        
    except Exception as e:
        logger.exception("Error during talent pool data synchronization")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@shared_task
def send_bulk_data_to_job_seeker(sync_job_id):
    """
    Task to send bulk data to the Job Seeker API.
    Implements retry and error handling.
    """
    MAX_RETRIES = 3
    
    db = SessionLocal()
    try:
        # Get the sync job
        sync_job = db.query(SyncJob).filter(SyncJob.id == sync_job_id).first()
        if not sync_job:
            logger.error(f"Sync job {sync_job_id} not found")
            return
        
        if sync_job.status == "success":
            logger.info(f"Sync job {sync_job_id} already completed successfully")
            return
        
        # Send data to Job Seeker Bulk API
        response = requests.post(
            settings.JOB_SEEKER_BULK_API_URL,
            json=sync_job.data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code in (200, 201, 202, 204):
            # Update sync job status
            sync_job.status = "success"
            db.commit()
            logger.info(f"Sync job {sync_job_id} completed successfully")
        else:
            # Handle error
            error_msg = f"API returned status code {response.status_code}: {response.text}"
            logger.warning(f"Sync job {sync_job_id} failed: {error_msg}")
            
            sync_job.retry_count += 1
            if sync_job.retry_count >= MAX_RETRIES:
                sync_job.status = "failed"
                sync_job.error_message = error_msg
            else:
                sync_job.error_message = error_msg
            
            db.commit()
            
            # If we haven't reached max retries, schedule a retry
            if sync_job.retry_count < MAX_RETRIES:
                send_bulk_data_to_job_seeker.apply_async(
                    args=[sync_job_id],
                    countdown=60 * (2 ** (sync_job.retry_count - 1))  # Exponential backoff
                )
    
    except Exception as e:
        logger.exception(f"Error in sync job {sync_job_id}")
        
        # Update sync job with error
        sync_job.retry_count += 1
        if sync_job.retry_count >= MAX_RETRIES:
            sync_job.status = "failed"
            sync_job.error_message = str(e)
        else:
            sync_job.error_message = str(e)
        
        db.commit()
        
        # If we haven't reached max retries, schedule a retry
        if sync_job.retry_count < MAX_RETRIES:
            send_bulk_data_to_job_seeker.apply_async(
                args=[sync_job_id],
                countdown=60 * (2 ** (sync_job.retry_count - 1))  # Exponential backoff
            )
    
    finally:
        db.close()

@shared_task
def retry_failed_sync_jobs():
    """
    Task to retry failed sync jobs that haven't reached max retries.
    """
    MAX_RETRIES = 3
    
    db = SessionLocal()
    try:
        # Find failed sync jobs with retry count less than max
        failed_jobs = db.query(SyncJob).filter(
            SyncJob.status == "failed",
            SyncJob.retry_count < MAX_RETRIES
        ).all()
        
        for job in failed_jobs:
            logger.info(f"Retrying failed sync job {job.id}")
            
            # Reset status to pending
            job.status = "pending"
            db.commit()
            
            # Schedule retry
            send_bulk_data_to_job_seeker.delay(job.id)
        
        return {"status": "success", "message": f"Scheduled {len(failed_jobs)} jobs for retry"}
    
    except Exception as e:
        logger.exception("Error during retry of failed sync jobs")
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()

def get_talent_pool_members(talent_pool_id):
    """
    Helper function to get members of a talent pool.
    In a real application, this would be a database query.
    This is a simplified example that returns mock data.
    """
    
    return [
        {
            "cvId": f"cv-{talent_pool_id}-1",
            "lastModifiedDt": "2025-01-29T09:49:41.228Z",
            "user": {
                "userId": f"user-{talent_pool_id}-1",
                "candidateCode": "WBJ-101"
            },
            "cvProfile": {
                "workingHours": 36,
                "willingToTravel": False
            },
            "cvAddress": {
                "geoLocation": [52.3730796, 4.8924534]
            },
            "cvItems": {
                "experience": [
                    {
                        "professionNm": "Data Consultant",
                        "company": "ABC Corp",
                        "startD": "2020-01-01",
                        "endD": "2022-12-31",
                        "location": "Amsterdam",
                        "description": "Worked on data analytics projects"
                    }
                ],
                "education": [
                    {
                        "educationalInstitutionNm": "University of Amsterdam",
                        "degreeCode": "MSc",
                        "degreeCodeJobDigger": "WO",
                        "fieldOfStudyNm": "Data Science",
                        "educationalInstitutionLocation": "Amsterdam",
                        "startD": "2015-09-01",
                        "endD": "2019-06-30",
                        "educationCompleted": True,
                        "educationSpecializationDescription": "Focus on machine learning"
                    }
                ]
            },
            "visibleInTalentPool": True,
            "applicationStatus": [
                {
                    "jobOfferCode": "2784631350_1",
                    "applicationStatus": "in-progress"
                }
            ],
            "matchFeedback": [
                {
                    "jobOfferCode": "2784631350_1",
                    "matchStatus": "good-match"
                }
            ]
        },
        # More members would be here in a real application
    ]