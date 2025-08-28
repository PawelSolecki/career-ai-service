from pydantic import BaseModel
from typing import List, Optional


class JobOffer(BaseModel):
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "technologies": self.technologies,
            "requirements": self.requirements,
            "responsibilities": self.responsibilities,
        }
