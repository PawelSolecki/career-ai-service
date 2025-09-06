from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date
from enum import Enum


class LanguageLevel(str, Enum):
    BASIC = "BASIC"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    NATIVE = "NATIVE"


class Level(str, Enum):
    JUNIOR = "JUNIOR"
    MID = "MID"
    SENIOR = "SENIOR"
    LEAD = "LEAD"
    PRINCIPAL = "PRINCIPAL"
    INTERN = "INTERN"


class UserCVSummary(BaseModel):
    text: Optional[str] = None
    tech: Optional[List[str]] = None


class UserCVPersonalInfo(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    other: Optional[str] = None


class UserCVExperience(BaseModel):
    position: Optional[str] = None
    company: Optional[str] = None
    url: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    summary: Optional[UserCVSummary] = None


class UserCVEducation(BaseModel):
    school: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class UserCVSkill(BaseModel):
    name: Optional[str] = None
    level: Optional[Level] = None
    years_of_experience: Optional[float] = None
    keywords: Optional[List[str]] = None


class UserCVLanguage(BaseModel):
    language: Optional[str] = None
    level: Optional[LanguageLevel] = None


class UserCVCertification(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[date] = None


class UserCVProject(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    technologies: Optional[List[str]] = None
    summary: Optional[UserCVSummary] = None


class UserCVInternship(BaseModel):
    position: Optional[str] = None
    company: Optional[str] = None
    url: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    summary: Optional[UserCVSummary] = None


class UserCV(BaseModel):
    personal_info: Optional[UserCVPersonalInfo] = None
    technologies: Optional[List[str]] = None
    experience: Optional[List[UserCVExperience]] = None
    education: Optional[List[UserCVEducation]] = None
    skills: Optional[List[UserCVSkill]] = None
    languages: Optional[List[UserCVLanguage]] = None
    certifications: Optional[List[UserCVCertification]] = None
    projects: Optional[List[UserCVProject]] = None
    internships: Optional[List[UserCVInternship]] = None
