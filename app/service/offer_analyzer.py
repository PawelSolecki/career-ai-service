from sentence_transformers import util
import numpy as np
from collections import defaultdict
from typing import Optional
from model.skill_result import SkillResult
from config.skill_config import hard_skills, soft_skills, tools
from util.embeddings import get_model


def analyze_job_offer(
    job_description: dict,
    alpha: float = 1.0,
    top_k: int = 5,
    max_results_per_category: Optional[int] = None,
) -> SkillResult:
    model = get_model()

    # Combine all skill categories
    all_skills = {
        "hard_skills": hard_skills,
        "soft_skills": soft_skills,
        "tools": tools,
    }

    # Create embeddings for all skills
    skill_embeddings = {}
    for category_name, skills_list in all_skills.items():
        for skill in skills_list:
            skill_embeddings[skill] = {
                "embedding": model.encode(skill, convert_to_tensor=True),
                "category": category_name,
            }

    final_scores = defaultdict(float)

    # Process all sections of job description
    for section, content in job_description.items():
        if content is None:
            continue

        # Handle both string and list content
        if isinstance(content, list):
            text = " ".join(content)
        else:
            text = str(content)

        sentences = text.split(".")
        for sentence in sentences:
            if sentence.strip() == "":
                continue
            sentence_emb = model.encode(sentence.strip(), convert_to_tensor=True)

            # Calculate similarities with all skills
            sims = []
            for skill, skill_data in skill_embeddings.items():
                similarity = util.cos_sim(sentence_emb, skill_data["embedding"]).item()
                sims.append((skill, similarity))

            sims.sort(key=lambda x: x[1], reverse=True)
            top_sims = sims[:top_k]

            # Calculate sentence weight
            sentence_weight = np.mean([s for _, s in top_sims])

            for skill, score in top_sims:
                boosted = score
                if score > 0.95:  # exact match
                    boosted *= 1 + alpha
                contribution = boosted * sentence_weight
                final_scores[skill] += contribution

    # Separate results by category
    categorized_scores = {"hard_skills": [], "soft_skills": [], "tools": []}

    for skill, score in final_scores.items():
        category = skill_embeddings[skill]["category"]
        categorized_scores[category].append((skill, score))

    # Sort each category by score
    for category in categorized_scores:
        categorized_scores[category].sort(key=lambda x: x[1], reverse=True)
        # Apply max_results_per_category limit if specified
        if max_results_per_category is not None:
            categorized_scores[category] = categorized_scores[category][
                :max_results_per_category
            ]

    return SkillResult(
        hard_skills=categorized_scores["hard_skills"],
        soft_skills=categorized_scores["soft_skills"],
        tools=categorized_scores["tools"],
    )
