from fastapi import APIRouter, HTTPException
from app.model.user_cv import UserCV
from app.model.job_offer import JobOffer
from app.model.skill_result import SkillResult
from app.service.cv_service import CVService

router = APIRouter()

# Utwórz instancję analizatora CV (singleton pattern dla lepszej wydajności)
cv_service = CVService()


@router.post("/analyze-cv", response_model=UserCV)
async def analyze_cv_endpoint(
    user_cv: UserCV,
    alpha: float = 1.0,
    top_k: int = 5,
    min_score: float = 0.1,
):
    try:
        enhanced_cv = cv_service.analyze_cv(
            user_cv, alpha=alpha, top_k=top_k, min_score=min_score
        )
        return enhanced_cv
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing CV: {str(e)}")


@router.post("/generate-bio")
async def generate_bio_endpoint(
    user_cv: UserCV,
    skill_result: SkillResult,
    job_offer: JobOffer,
):
    try:
        bio = cv_service.generate_bio(user_cv, skill_result, job_offer)
        return {"bio": bio}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating bio: {str(e)}")
