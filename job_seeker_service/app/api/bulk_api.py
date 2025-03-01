from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import logging
from typing import List

from app.database import get_db
from app.api.schemas import BulkSyncRequest, ProfileCreate
from app.services.matching_service import sync_profile_to_matching_partner
from app.models.profile import (
    User, CVProfile, CVAddress, Experience, Education, Hobby, 
    Language, SoftSkill, Certificate, TalentPoolMembership,
    ApplicationStatus, MatchFeedback, ProfileChangeLog
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/bulk", status_code=202)
async def receive_bulk_data(
    bulk_data: BulkSyncRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Bulk API to receive talent pool data, including member details and job match feedback.
    This endpoint processes the data asynchronously and syncs relevant changes to the matching partner.
    """
    try:
        for profile_data in bulk_data.profiles:
            # Process each profile
            process_profile(db, profile_data, background_tasks)
        
        return {"message": "Bulk data received and processing started"}
    except Exception as e:
        logger.error(f"Error processing bulk data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing bulk data: {str(e)}")

def process_profile(db: Session, profile_data: ProfileCreate, background_tasks: BackgroundTasks):
    
    """Process individual profile data from bulk request"""
    
    # Check if profile exists
    profile = db.query(CVProfile).filter(CVProfile.cv_id == profile_data.cvId).first()
    
    if profile:
        # Update existing profile
        update_profile(db, profile, profile_data)
        operation = "UPDATE"
    else:
        # Create new profile
        profile = create_profile(db, profile_data)
        operation = "INSERT"
    
    # Log the change
    log_entry = ProfileChangeLog(
        cv_id=profile_data.cvId,
        operation=operation,
        synced_to_matching_partner=False,
        payload=profile_data.dict()
    )
    db.add(log_entry)
    db.commit()
    
    # Trigger sync to matching partner in background
    background_tasks.add_task(
        sync_profile_to_matching_partner, 
        profile_id=profile.cv_id, 
        operation=operation,
        db=db
    )

def create_profile(db: Session, profile_data: ProfileCreate) -> CVProfile:
    """Create a new profile from request data"""
    
    # Create user
    user = User(
        user_id=profile_data.user.userId,
        candidate_code=profile_data.user.candidateCode
    )
    db.add(user)
    db.flush()  # Flush to get the user ID
    
    # Create CV profile
    profile = CVProfile(
        cv_id=profile_data.cvId,
        last_modified_dt=profile_data.lastModifiedDt,
        user_id=user.id,
        working_hours=profile_data.cvProfile.workingHours,
        willing_to_travel=profile_data.cvProfile.willingToTravel,
        visible_in_talent_pool=profile_data.visibleInTalentPool
    )
    db.add(profile)
    db.flush()  # Flush to get the profile ID
    
    # Create CV address
    if profile_data.cvAddress and profile_data.cvAddress.geoLocation:
        address = CVAddress(
            profile_id=profile.id,
            geo_location=profile_data.cvAddress.geoLocation
        )
        db.add(address)
    
    # Process CV items
    if profile_data.cvItems:
        # Add experiences
        if "experience" in profile_data.cvItems:
            for exp_data in profile_data.cvItems["experience"]:
                exp = Experience(
                    profile_id=profile.id,
                    profession_nm=exp_data["professionNm"],
                    company=exp_data["company"],
                    start_d=exp_data.get("startD"),
                    end_d=exp_data.get("endD"),
                    location=exp_data.get("location"),
                    description=exp_data.get("description")
                )
                db.add(exp)
        
        # Add educations
        if "education" in profile_data.cvItems:
            for edu_data in profile_data.cvItems["education"]:
                edu = Education(
                    profile_id=profile.id,
                    educational_institution_nm=edu_data["educationalInstitutionNm"],
                    degree_code=edu_data["degreeCode"],
                    degree_code_job_digger=edu_data["degreeCodeJobDigger"],
                    field_of_study_nm=edu_data["fieldOfStudyNm"],
                    educational_institution_location=edu_data["educationalInstitutionLocation"],
                    start_d=edu_data.get("startD"),
                    end_d=edu_data.get("endD"),
                    education_completed=edu_data.get("educationCompleted"),
                    education_specialization_description=edu_data.get("educationSpecializationDescription")
                )
                db.add(edu)
        
        # Add hobbies
        if "hobby" in profile_data.cvItems:
            for hobby_data in profile_data.cvItems["hobby"]:
                hobby = Hobby(
                    profile_id=profile.id,
                    hobby_nm=hobby_data["hobbyNm"]
                )
                db.add(hobby)
        
        # Add languages
        if "language" in profile_data.cvItems:
            for lang_data in profile_data.cvItems["language"]:
                lang = Language(
                    profile_id=profile.id,
                    skill_nm=lang_data["skillNm"],
                    rating=lang_data.get("rating")
                )
                db.add(lang)
        
        # Add soft skills
        if "softSkillKnowledge" in profile_data.cvItems:
            for skill_data in profile_data.cvItems["softSkillKnowledge"]:
                skill = SoftSkill(
                    profile_id=profile.id,
                    skill_id=skill_data["skillId"],
                    skill_nm=skill_data["skillNm"],
                    related_line_item_type=skill_data.get("relatedLineItemType"),
                    rating=skill_data.get("rating")
                )
                db.add(skill)
        
        # Add certificates
        if "certificate" in profile_data.cvItems:
            for cert_data in profile_data.cvItems["certificate"]:
                cert = Certificate(
                    profile_id=profile.id,
                    certificate_id=cert_data["certificateId"],
                    skill_nm=cert_data["skillNm"]
                )
                db.add(cert)
    
    # Add talent pool memberships
    if profile_data.memberOf:
        for membership_data in profile_data.memberOf:
            membership = TalentPoolMembership(
                profile_id=profile.id,
                talent_pool_id=membership_data.talentPoolId,
                talent_pool_name=membership_data.talentPoolName
            )
            db.add(membership)
    
    # Add application statuses
    if profile_data.applicationStatus:
        for status_data in profile_data.applicationStatus:
            status = ApplicationStatus(
                profile_id=profile.id,
                job_offer_code=status_data.jobOfferCode,
                application_status=status_data.applicationStatus
            )
            db.add(status)
    
    # Add match feedbacks
    if profile_data.matchFeedback:
        for feedback_data in profile_data.matchFeedback:
            feedback = MatchFeedback(
                profile_id=profile.id,
                job_offer_code=feedback_data.jobOfferCode,
                match_status=feedback_data.matchStatus
            )
            db.add(feedback)
    
    db.commit()
    return profile

def update_profile(db: Session, profile: CVProfile, profile_data: ProfileCreate):
    """Update an existing profile with new data"""
    
    # Update basic profile info
    profile.last_modified_dt = profile_data.lastModifiedDt
    profile.working_hours = profile_data.cvProfile.workingHours
    profile.willing_to_travel = profile_data.cvProfile.willingToTravel
    profile.visible_in_talent_pool = profile_data.visibleInTalentPool
    
    # Update user info
    if profile.user:
        profile.user.user_id = profile_data.user.userId
        profile.user.candidate_code = profile_data.user.candidateCode
    
    # Update address
    if profile_data.cvAddress and profile_data.cvAddress.geoLocation:
        if profile.address:
            profile.address.geo_location = profile_data.cvAddress.geoLocation
        else:
            address = CVAddress(
                profile_id=profile.id,
                geo_location=profile_data.cvAddress.geoLocation
            )
            db.add(address)
    
    db.query(Experience).filter(Experience.profile_id == profile.id).delete()
    db.query(Education).filter(Education.profile_id == profile.id).delete()
    db.query(Hobby).filter(Hobby.profile_id == profile.id).delete()
    db.query(Language).filter(Language.profile_id == profile.id).delete()
    db.query(SoftSkill).filter(SoftSkill.profile_id == profile.id).delete()
    db.query(Certificate).filter(Certificate.profile_id == profile.id).delete()
    db.query(TalentPoolMembership).filter(TalentPoolMembership.profile_id == profile.id).delete()
    db.query(ApplicationStatus).filter(ApplicationStatus.profile_id == profile.id).delete()
    db.query(MatchFeedback).filter(MatchFeedback.profile_id == profile.id).delete()
    
    # Re-add all items using the same logic as in create_profile
    if profile_data.cvItems:
        # Add experiences
        if "experience" in profile_data.cvItems:
            for exp_data in profile_data.cvItems["experience"]:
                exp = Experience(
                    profile_id=profile.id,
                    profession_nm=exp_data["professionNm"],
                    company=exp_data["company"],
                    start_d=exp_data.get("startD"),
                    end_d=exp_data.get("endD"),
                    location=exp_data.get("location"),
                    description=exp_data.get("description")
                )
                db.add(exp)
        
        # Add educations, hobbies, languages, soft skills, certificates...
        # (Similar code as in create_profile for each type)
        # ...
    
    # Add talent pool memberships, application statuses, match feedbacks
    # (Similar code as in create_profile for each type)
    # ...
    
    db.commit()
    return profile