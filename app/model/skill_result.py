from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SkillResult:
    hard_skills: List[Tuple[str, float]]
    soft_skills: List[Tuple[str, float]]
    tools: List[Tuple[str, float]]
