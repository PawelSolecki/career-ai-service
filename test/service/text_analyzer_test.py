import pytest
from unittest.mock import MagicMock
from app.service.text_analyzer import TextAnalyzer
from app.model.skill_result import SkillItem, SkillResult


class MockTensor:
    """Mock tensor-like object that has an item() method"""

    def __init__(self, value):
        self.value = value

    def item(self):
        return self.value


@pytest.fixture
def mock_text_analyzer(monkeypatch):
    mock_model = MagicMock()

    # Mock the model to return tensor-like objects
    mock_model.encode.return_value = [1.0, 0.0, 0.0]

    monkeypatch.setattr("app.service.text_analyzer.get_model", lambda: mock_model)

    analyzer = TextAnalyzer()

    # Set embeddings to simple lists (they don't need .item() method)
    for skill, data in analyzer.skill_embeddings.items():
        data["embedding"] = [1.0, 0.0, 0.0]

    return analyzer


def test_extract_skills_empty_text(mock_text_analyzer):
    skills = mock_text_analyzer.extract_skills_from_text("")
    assert skills == []


def test_extract_skills_no_matches(monkeypatch, mock_text_analyzer):

    monkeypatch.setattr(
        "app.service.text_analyzer.util.cos_sim", lambda a, b: MockTensor(0.1)
    )
    skills = mock_text_analyzer.extract_skills_from_text("Some text")
    assert skills == []


def test_extract_skills_with_matches(monkeypatch, mock_text_analyzer):
    monkeypatch.setattr(
        "app.service.text_analyzer.util.cos_sim", lambda a, b: MockTensor(0.9)
    )
    skills = mock_text_analyzer.extract_skills_from_text(
        "Worked with Python", similarity_threshold=0.5
    )
    assert all(isinstance(s, SkillItem) for s in skills)
    assert len(skills) > 0


def test_analyze_multiple_texts(mock_text_analyzer, monkeypatch):
    monkeypatch.setattr(
        "app.service.text_analyzer.util.cos_sim", lambda a, b: MockTensor(0.95)
    )
    result = mock_text_analyzer.analyze_multiple_texts(
        ["Python project", "Another with Python"], top_k=2, max_results_per_category=1
    )

    assert isinstance(result, dict)
    assert set(result.keys()) == {"hard_skills", "soft_skills", "tools"}

    assert any(len(v) > 0 for v in result.values())
