import uuid
from sqlalchemy import Boolean, Column, String, Integer, Float, ARRAY, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, unique=True, index=True)
    candidate_code = Column(String, index=True)
    
    profile = relationship("CVProfile", back_populates="user", uselist=False)

class CVProfile(Base):
    __tablename__ = "cv_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cv_id = Column(String, unique=True, index=True)
    last_modified_dt = Column(DateTime, default=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    working_hours = Column(Integer)
    willing_to_travel = Column(Boolean, default=False)
    visible_in_talent_pool = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="profile")
    address = relationship("CVAddress", back_populates="profile", uselist=False)
    experiences = relationship("Experience", back_populates="profile")
    educations = relationship("Education", back_populates="profile")
    hobbies = relationship("Hobby", back_populates="profile")
    languages = relationship("Language", back_populates="profile")
    soft_skills = relationship("SoftSkill", back_populates="profile")
    certificates = relationship("Certificate", back_populates="profile")
    talent_pools = relationship("TalentPoolMembership", back_populates="profile")
    application_statuses = relationship("ApplicationStatus", back_populates="profile")
    match_feedbacks = relationship("MatchFeedback", back_populates="profile")

class CVAddress(Base):
    __tablename__ = "cv_addresses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("cv_profiles.id"))
    geo_location = Column(ARRAY(Float), nullable=True)
    
    profile = relationship("CVProfile", back_populates="address")

class Experience(Base):
    __tablename__ = "experiences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("cv_profiles.id"))
    profession_nm = Column(String)
    company = Column(String)
    start_d = Column(String, nullable=True)
    end_d = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(String, nullable=True)
    
    profile = relationship("CVProfile", back_populates="experiences")

class Education(Base):
    __tablename__ = "educations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("cv_profiles.id"))
    educational_institution_nm = Column(String)
    degree_code = Column(String)
    degree_code_job_digger = Column(String)
    field_of_study_nm = Column(String)
    educational_institution_location = Column(String)
    start_d = Column(String, nullable=True)
    end_d = Column(String, nullable=True)
    education_completed = Column(Boolean, nullable=True)
    education_specialization_description = Column(String, nullable=True)
    
    profile = relationship("CVProfile", back_populates="educations")

class Hobby(Base):
    __tablename__ = "hobbies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("cv_profiles.id"))
    hobby_nm = Column(String)
    
    profile = relationship("CVProfile", back_populates="hobbies")

class Language(Base):
    __tablename__ = "languages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("cv_profiles.id"))
    skill_nm = Column(String)
    rating = Column(Integer, nullable=True)
    
    profile = relationship("CVProfile", back_populates="languages")

class SoftSkill(Base):
    __tablename__ = "soft_skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("cv_profiles.id"))
    skill_id = Column(String)
    skill_nm = Column(String)
    related_line_item_type = Column(ARRAY(String), nullable=True)
    rating = Column(Integer, nullable=True)
    
    profile = relationship("CVProfile", back_populates="soft_skills")

class Certificate(Base):
    __tablename__ = "certificates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("cv_profiles.id"))
    certificate_id = Column(String)
    skill_nm = Column(String)
    
    profile = relationship("CVProfile", back_populates="certificates")

class TalentPoolMembership(Base):
    __tablename__ = "talent_pool_memberships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("cv_profiles.id"))
    talent_pool_id = Column(String)
    talent_pool_name = Column(String)
    
    profile = relationship("CVProfile", back_populates="talent_pools")

class ApplicationStatus(Base):
    __tablename__ = "application_statuses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("cv_profiles.id"))
    job_offer_code = Column(String)
    application_status = Column(String)
    
    profile = relationship("CVProfile", back_populates="application_statuses")

class MatchFeedback(Base):
    __tablename__ = "match_feedbacks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("cv_profiles.id"))
    job_offer_code = Column(String)
    match_status = Column(String)
    
    profile = relationship("CVProfile", back_populates="match_feedbacks")

class ProfileChangeLog(Base):
    __tablename__ = "profile_change_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cv_id = Column(String, index=True)
    operation = Column(String)  # INSERT, UPDATE, DELETE
    timestamp = Column(DateTime, default=datetime.utcnow)
    synced_to_matching_partner = Column(Boolean, default=False)
    payload = Column(JSON, nullable=True)