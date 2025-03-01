# This file marks the models directory as a Python package
# Import models to make them available when importing the package
from app.models.profile import (
    User, CVProfile, CVAddress, Experience, Education, 
    Hobby, Language, SoftSkill, Certificate, 
    TalentPoolMembership, ApplicationStatus, MatchFeedback,
    ProfileChangeLog
)