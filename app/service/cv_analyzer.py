from typing import List, Optional
from app.model.user_cv import UserCV
from app.model.skill_result import SkillItem
from app.service.text_analyzer import TextAnalyzer


class CVAnalyzer:
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
        enhanced_cv = cv.copy(deep=True)

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
