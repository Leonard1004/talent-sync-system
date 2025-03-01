from typing import List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class UserBase(BaseModel):
    userId: str
    candidateCode: str

class GeoLocation(BaseModel):
    geoLocation: Optional[List[float]]

class ExperienceBase(BaseModel):
    professionNm: str
    company: str
    startD: Optional[str] = None
    endD: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

class EducationBase(BaseModel):
    educationalInstitutionNm: str
    degreeCode: str
    degreeCodeJobDigger: str
    fieldOfStudyNm: str
    educationalInstitutionLocation: str
    startD: Optional[str] = None
    endD: Optional[str] = None
    educationCompleted: Optional[bool] = None
    educationSpecializationDescription: Optional[str] = None

class HobbyBase(BaseModel):
    hobbyNm: str

class LanguageBase(BaseModel):
    skillNm: str
    rating: Optional[int] = None

class SoftSkillBase(BaseModel):
    skillId: str
    skillNm: str
    relatedLineItemType: Optional[List[str]] = []
    rating: Optional[int] = None

class CertificateBase(BaseModel):
    certificateId: str
    skillNm: str

class TalentPoolMembershipBase(BaseModel):
    talentPoolId: str
    talentPoolName: str

class ApplicationStatusBase(BaseModel):
    jobOfferCode: str
    applicationStatus: str

class MatchFeedbackBase(BaseModel):
    jobOfferCode: str
    matchStatus: str

class CVProfileBase(BaseModel):
    workingHours: int
    willingToTravel: bool

class ProfileCreate(BaseModel):
    cvId: str
    lastModifiedDt: datetime
    user: UserBase
    cvProfile: CVProfileBase
    cvAddress: GeoLocation
    cvItems: dict
    visibleInTalentPool: bool
    memberOf: Optional[List[TalentPoolMembershipBase]] = []
    applicationStatus: Optional[List[ApplicationStatusBase]] = []
    matchFeedback: Optional[List[MatchFeedbackBase]] = []

class BulkSyncRequest(BaseModel):
    profiles: List[ProfileCreate]

class ProfileChangeNotification(BaseModel):
    cvId: str
    operation: str  # INSERT, UPDATE, DELETE
    profile: Optional[dict] = None