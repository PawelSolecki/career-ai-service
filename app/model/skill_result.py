from dataclasses import dataclass
from typing import List


@dataclass
class SkillItem:
    name: str
    score: float


@dataclass
class SkillResult:
    hard_skills: List[SkillItem]
    soft_skills: List[SkillItem]
    tools: List[SkillItem]
