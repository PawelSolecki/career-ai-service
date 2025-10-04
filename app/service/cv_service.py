from app.model.user_cv import UserCV
from app.service.text_analyzer import TextAnalyzer
from app.model.skill_result import SkillResult
from app.model.job_offer import JobOffer
import json
import requests
import os
from fastapi import HTTPException

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "prompt.json")
OLLAMA_URL = "http://ollama:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"


class CVService:
    def __init__(self):
        self.text_analyzer = TextAnalyzer()

    def analyze_cv(
        self,
        cv: UserCV,
        alpha: float,
        top_k: int,
        min_score: float,
    ) -> UserCV:
        """
        Analyzes a user's CV and detects technologies in Summary.text,
        then adds them to Summary.technologies.

        Args:
            cv: User's CV to analyze
            alpha: Boosting factor for exact matches
            top_k: Number of best matches to consider per sentence
            min_score: Minimum score for including technologies

        Returns:
            CV with detected technologies in Summary.technologies
        """
        enhanced_cv = cv.model_copy(deep=True)

        # Analyze summaries in experiences
        if enhanced_cv.experience:
            for experience in enhanced_cv.experience:
                if experience.summaries:
                    for summary in experience.summaries:
                        self._analyze_summary(summary, alpha, top_k, min_score)

        # Analyze summaries in projects
        if enhanced_cv.projects:
            for project in enhanced_cv.projects:
                if project.summaries:
                    for summary in project.summaries:
                        self._analyze_summary(summary, alpha, top_k, min_score)

        return enhanced_cv

    def generate_bio(
        self,
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
        try:
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
                "experience_years": 0,
                "skills": [
                    {"name": skill, "level": "", "years_of_experience": 0}
                    for skill in (user_cv.skills or [])
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
                    [skill.name, skill.score]
                    for skill in (skill_result.hard_skills or [])
                ],
                "soft_skills": [
                    [skill.name, skill.score]
                    for skill in (skill_result.soft_skills or [])
                ],
                "tools": [
                    [skill.name, skill.score] for skill in (skill_result.tools or [])
                ],
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

            print(payload)
            response = requests.post(llama_url, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            print("response", response)
            print("result", result)
            bio = result.get("response", "")

            if not bio:
                raise ValueError("Empty response from Ollama service")

            return bio
        except requests.Timeout:
            raise HTTPException(
                status_code=504,
                detail="Request to Ollama service timed out. Please try again later.",
            )
        except requests.ConnectionError:
            raise HTTPException(
                status_code=503,
                detail="Could not connect to Ollama service. Service might be unavailable.",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error generating bio: {str(e)}"
            )

    def _analyze_summary(
        self, summary: UserCV.Summary, alpha: float, top_k: int, min_score: float
    ) -> None:
        """
        Analyzes a single Summary.text and adds detected technologies to Summary.technologies.

        Args:
            summary: Summary to analyze (modified in-place)
            alpha: Boosting factor for exact matches
            top_k: Number of best matches to consider per sentence
            min_score: Minimum score for including technologies
        """
        if not summary.text or not summary.text.strip():
            return

        # Detect technologies from text
        detected_skills = self.text_analyzer.extract_skills_from_text(
            summary.text, alpha, top_k
        )

        # Filter by minimum score and take only names (without score)
        detected_tech_names = [
            skill.name for skill in detected_skills if skill.score >= min_score
        ]

        if detected_tech_names:
            if summary.technologies:
                # Add new technologies, avoiding duplicates and preserving order
                existing_tech = set(summary.technologies)
                new_tech = [
                    tech for tech in detected_tech_names if tech not in existing_tech
                ]
                summary.technologies.extend(new_tech)
            else:
                # Create a new list of technologies
                summary.technologies = detected_tech_names
