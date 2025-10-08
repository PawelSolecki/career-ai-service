from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
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
        firstName: str
        lastName: str
        email: Optional[EmailStr] = None
        phone: Optional[str] = None
        role: Optional[str] = None
        summary: Optional[str] = None
        linkedIn: Optional[str] = None
        github: Optional[str] = None
        website: Optional[str] = None
        other: Optional[str] = None

        @field_validator("firstName", "lastName")
        @classmethod
        def validate_required_fields(cls, v: str) -> str:
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
        startDate: Optional[Date] = None
        endDate: Optional[Date] = None
        summaries: Optional[List["UserCV.Summary"]] = None

        model_config = ConfigDict(arbitrary_types_allowed=True)

    class Education(BaseModel):
        school: Optional[str] = None
        degree: Optional[str] = None
        fieldOfStudy: Optional[str] = None
        startDate: Optional[Date] = None
        endDate: Optional[Date] = None

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

        model_config = ConfigDict(arbitrary_types_allowed=True)

    personalInfo: PersonalInfo
    skills: Optional[List[str]] = None
    experience: Optional[List[Experience]] = None
    education: Optional[List[Education]] = None
    languages: Optional[List[Language]] = None
    certifications: Optional[List[Certification]] = None
    projects: Optional[List[Project]] = None

    @field_validator("personalInfo")
    @classmethod
    def validate_personal_info(cls, v: PersonalInfo) -> PersonalInfo:
        if v is None:
            raise ValueError("Personal info is required")
        return v

    model_config = ConfigDict(arbitrary_types_allowed=True)


# Initialize models with circular references
UserCV.model_rebuild()
