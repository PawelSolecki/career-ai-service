from app.model.user_cv import UserCV
from app.model.job_offer import JobOffer
from app.model.skill_result import SkillResult
from pydantic import BaseModel


class GenerateBioRequest(BaseModel):
    user_cv: UserCV
    skill_result: SkillResult
    job_offer: JobOffer
    language: str = "en"
