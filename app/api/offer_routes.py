from fastapi import APIRouter, HTTPException, Query
from model.job_offer import JobOffer
from model.skill_result import SkillResult
from model.user_cv import UserCV
from service.offer_analyzer import analyze_job_offer
from service.bio_generator import generate_bio
from typing import Optional

router = APIRouter()


@router.post("/analyze-offer", response_model=SkillResult)
async def analyze_job_offer_endpoint(
    job_offer: JobOffer,
    max_results_per_category: Optional[int] = Query(
        None, description="Maximum number of results per category"
    ),
):
    try:
        job_data = job_offer.to_dict()
        result = analyze_job_offer(
            job_data, max_results_per_category=max_results_per_category
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error analyzing job offer: {str(e)}"
        )

@router.post("/generate-bio")
async def generate_bio_endpoint(
    user_cv: UserCV,
    skill_result: SkillResult,
    job_offer: JobOffer,
):
    """
    Generate a professional bio for a candidate tailored to a specific job offer using Llama.
    """
    try:
        bio = generate_bio(user_cv, skill_result, job_offer)
        return {"bio": bio}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating bio: {str(e)}"
        )
