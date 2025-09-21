from sentence_transformers import util
import numpy as np
from collections import defaultdict
from typing import Dict, List, Optional, Any
from app.model.skill_result import SkillItem
from app.config.skill_config import hard_skills, soft_skills, tools
from app.util.embeddings import get_model


class TextAnalyzer:
    def __init__(self):
        self.model = get_model()
        self.skill_embeddings = self._prepare_skill_embeddings()

    def _prepare_skill_embeddings(self) -> Dict[str, Dict[str, Any]]:
        all_skills = {
            "hard_skills": hard_skills,
            "soft_skills": soft_skills,
            "tools": tools,
        }

        skill_embeddings = {}
        for category_name, skills_list in all_skills.items():
            for skill in skills_list:
                skill_embeddings[skill] = {
                    "embedding": self.model.encode(skill, convert_to_tensor=True),
                    "category": category_name,
                }
        return skill_embeddings

    def extract_skills_from_text(
        self,
        text: str,
        alpha: float = 1.0,
        top_k: int = 5,
        similarity_threshold: float = 0.3,
    ) -> List[SkillItem]:
        """
        Extracts skills from a single text.

        Args:
            text: text to analyze
            alpha: Boosting factor for exact matches
            top_k: Number of best matches to consider per sentence
            similarity_threshold: Minimum similarity threshold for including a skill

        Returns:
            List of SkillItem with detected skills
        """
        if not text or not text.strip():
            return []

        final_scores = defaultdict(float)
        sentences = text.split(".")

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_emb = self.model.encode(sentence, convert_to_tensor=True)

            sims = []
            for skill, skill_data in self.skill_embeddings.items():
                similarity = util.cos_sim(sentence_emb, skill_data["embedding"]).item()
                if similarity >= similarity_threshold:
                    sims.append((skill, similarity))

            if not sims:
                continue

            sims.sort(key=lambda x: x[1], reverse=True)
            top_sims = sims[:top_k]

            sentence_weight = np.mean([s for _, s in top_sims])

            for skill, score in top_sims:
                boosted = score
                if score > 0.95:
                    boosted *= 1 + alpha
                contribution = boosted * sentence_weight
                final_scores[skill] += contribution

        skills = []
        for skill, score in final_scores.items():
            if score > 0:
                skills.append(SkillItem(name=skill, score=score))

        skills.sort(key=lambda x: x.score, reverse=True)
        return skills

    def analyze_multiple_texts(
        self,
        texts: List[str],
        alpha: float = 1.0,
        top_k: int = 5,
        max_results_per_category: Optional[int] = None,
    ) -> Dict[str, List[SkillItem]]:
        """
        Analyzes multiple texts and aggregates skill scores.

        Args:
            texts: List of texts to analyze
            alpha: Boosting factor for exact matches
            top_k: Number of best matches to consider per sentence
            max_results_per_category: Maximum number of results per category

        Returns:
            Dictionary with skills grouped by category
        """
        final_scores = defaultdict(float)

        for text in texts:
            if not text or not text.strip():
                continue

            skills = self.extract_skills_from_text(text, alpha, top_k)
            for skill in skills:
                final_scores[skill.name] += skill.score

        categorized_scores = {"hard_skills": [], "soft_skills": [], "tools": []}

        for skill, score in final_scores.items():
            if skill in self.skill_embeddings:
                category = self.skill_embeddings[skill]["category"]
                categorized_scores[category].append(SkillItem(name=skill, score=score))

        for category in categorized_scores:
            categorized_scores[category].sort(key=lambda x: x.score, reverse=True)
            if max_results_per_category is not None:
                categorized_scores[category] = categorized_scores[category][
                    :max_results_per_category
                ]

        return categorized_scores
