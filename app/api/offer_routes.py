from fastapi import APIRouter, HTTPException, Query
from model.job_offer import JobOffer
from model.skill_result import SkillResult
from service.offer_analyzer import analyze_job_offer
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
