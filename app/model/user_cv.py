from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import date as Date
from enum import Enum


class LanguageLevel(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class UserCV(BaseModel):
    class PersonalInfo(BaseModel):
        first_name: str
        last_name: str
        email: Optional[EmailStr] = None
        phone: Optional[str] = None
        role: Optional[str] = None
        summary: Optional[str] = None
        linked_in: Optional[str] = None
        github: Optional[str] = None
        website: Optional[str] = None
        other: Optional[str] = None

        @validator("first_name", "last_name")
        def validate_required_fields(cls, v):
            if not v or not v.strip():
                raise ValueError("Field is required")
            return v

    class Summary(BaseModel):
        text: Optional[str] = None
        technologies: Optional[List[str]] = None

    class Experience(BaseModel):
        position: Optional[str] = None
        company: Optional[str] = None
        url: Optional[str] = None
        location: Optional[str] = None
        start_date: Optional[Date] = None
        end_date: Optional[Date] = None
        summaries: Optional[List["UserCV.Summary"]] = None

    class Education(BaseModel):
        school: Optional[str] = None
        degree: Optional[str] = None
        field_of_study: Optional[str] = None
        start_date: Optional[Date] = None
        end_date: Optional[Date] = None

    class Language(BaseModel):
        language: Optional[str] = None
        level: Optional[LanguageLevel] = None

    class Certification(BaseModel):
        name: Optional[str] = None
        issuer: Optional[str] = None
        date: Optional[Date] = None

    class Project(BaseModel):
        name: Optional[str] = None
        url: Optional[str] = None
        summaries: Optional[List["UserCV.Summary"]] = None

    personal_info: PersonalInfo
    skills: Optional[List[str]] = None
    experience: Optional[List[Experience]] = None
    education: Optional[List[Education]] = None
    languages: Optional[List[Language]] = None
    certifications: Optional[List[Certification]] = None
    projects: Optional[List[Project]] = None

    @validator("personal_info")
    def validate_personal_info(cls, v):
        if v is None:
            raise ValueError("Personal info is required")
        return v


UserCV.Experience.update_forward_refs()
UserCV.Project.update_forward_refs()
