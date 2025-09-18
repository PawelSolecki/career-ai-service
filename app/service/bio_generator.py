from app.model.user_cv import UserCV
from app.model.skill_result import SkillResult
from app.model.job_offer import JobOffer
import json
import requests
import os

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "prompt.json")
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"


def generate_bio(
    user_cv: UserCV,
    skill_result: SkillResult,
    job_offer: JobOffer,
    prompt_path: str = PROMPT_PATH,
    llama_url: str = OLLAMA_URL,
) -> str:
    """
    Generate a professional bio for a candidate tailored to a specific job offer using Llama.

    Args:
        user_cv (UserCV): Candidate CV data.
        skill_result (SkillResult): Skills analysis result.
        job_offer (JobOffer): Job offer data.
        prompt_path (str): Path to the prompt file.
        llama_url (str): URL of the locally hosted Llama server.

    Returns:
        str: Generated bio text.
    """
    # Load prompt template
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_data = json.load(f)

    # Prepare UserCV data for Llama
    personal_info = user_cv.personal_info or {}
    usercv_payload = {
        "personal_info": {
            "first_name": getattr(personal_info, "first_name", ""),
            "last_name": getattr(personal_info, "last_name", ""),
        },
        "role": getattr(personal_info, "summary", "") or "",
        "experience_years": max(
            [s.years_of_experience or 0 for s in (user_cv.skills or [])], default=0
        ),
        "skills": [
            {
                "name": s.name or "",
                "level": s.level.value if s.level else "",
                "years_of_experience": s.years_of_experience or 0,
            }
            for s in (user_cv.skills or [])
        ],
    }

    # Prepare JobOffer data for Llama
    job_offer_payload = {
        "description": job_offer.description or "",
        "technologies": job_offer.technologies or [],
        "requirements": job_offer.requirements or [],
        "responsibilities": job_offer.responsibilities or [],
    }

    # Prepare SkillResult data for Llama
    skill_result_payload = {
        "hard_skills": [
            [skill.name, skill.score] for skill in (skill_result.hard_skills or [])
        ],
        "soft_skills": [
            [skill.name, skill.score] for skill in (skill_result.soft_skills or [])
        ],
        "tools": [[skill.name, skill.score] for skill in (skill_result.tools or [])],
    }

    llama_payload = {
        "instructions": prompt_data.get("instructions", {}),
        "UserCV": usercv_payload,
        "JobOffer": job_offer_payload,
        "SkillResult": skill_result_payload,
    }

    # Send request to locally hosted Llama server
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": json.dumps(llama_payload),
        "stream": False,
    }
    response = requests.post(llama_url, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    bio = result.get("response", "")
    return bio
