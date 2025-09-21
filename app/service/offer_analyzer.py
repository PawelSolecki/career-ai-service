from typing import Optional
from app.model.skill_result import SkillResult
from app.service.text_analyzer import TextAnalyzer


class OfferAnalyzer:
    """
    Serwis do analizowania ofert pracy i wyekstraktowania umiejętności.
    """

    def __init__(self):
        self.text_analyzer = TextAnalyzer()

    def analyze_job_offer(
        self,
        job_description: dict,
        alpha: float = 1.0,
        top_k: int = 5,
        max_results_per_category: Optional[int] = None,
    ) -> SkillResult:
        """
        Analyzes a job offer and extracts skills.

        Args:
            job_description: Dictionary with job offer description
            alpha: Boosting factor for exact matches
            top_k: Number of best matches to consider per sentence
            max_results_per_category: Maximum number of results per category

        Returns:
            SkillResult with detected skills grouped by category
        """
        # Extract texts from structured job description content
        texts = []
        for section, section_content in job_description.items():
            if section_content is None:
                continue

            # Handle both string and list cases
            if isinstance(section_content, list):
                text = " ".join(str(item) for item in section_content)
            else:
                text = str(section_content)

            if text.strip():
                texts.append(text)

        # Analyze extracted texts
        categorized_scores = self.text_analyzer.analyze_multiple_texts(
            texts, alpha, top_k, max_results_per_category
        )

        return SkillResult(
            hard_skills=categorized_scores["hard_skills"],
            soft_skills=categorized_scores["soft_skills"],
            tools=categorized_scores["tools"],
        )
