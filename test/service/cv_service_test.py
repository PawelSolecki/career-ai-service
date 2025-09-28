import pytest
from unittest.mock import MagicMock
from app.service.cv_service import CVService
from app.model.user_cv import UserCV
from app.model.skill_result import SkillResult, SkillItem


@pytest.fixture
def sample_cv():
    return UserCV(
        personal_info=UserCV.PersonalInfo(first_name="Jan", last_name="Kowalski"),
        experience=[
            UserCV.Experience(
                summaries=[
                    UserCV.Summary(text="Worked with Python and Excel", technologies=[])
                ]
            )
        ],
        projects=[],
    )


@pytest.fixture
def mock_analyzer(monkeypatch):
    mock = MagicMock()
    mock.extract_skills_from_text.return_value = [
        SkillItem(name="Python", score=0.9),
        SkillItem(name="Communication", score=0.7),
        SkillItem(name="Excel", score=0.3),  # poniżej progu
    ]
    monkeypatch.setattr("app.service.cv_service.TextAnalyzer", lambda: mock)
    return mock


def test_analyze_cv_adds_technologies(sample_cv, mock_analyzer):
    service = CVService()
    result = service.analyze_cv(sample_cv, alpha=1.0, top_k=3, min_score=0.5)

    techs = []
    if result.experience and result.experience[0].summaries:
        techs = result.experience[0].summaries[0].technologies or []

    assert "Python" in techs
    assert "Communication" in techs
    assert "Excel" not in techs  # score < 0.5


def test_analyze_summary_empty_text(sample_cv, mock_analyzer):
    sample_cv.experience[0].summaries[0].text = "   "  # tylko spacje
    service = CVService()
    result = service.analyze_cv(sample_cv, alpha=1.0, top_k=3, min_score=0.5)

    assert (
        result.experience
        and result.experience[0].summaries
        and result.experience[0].summaries[0].technologies == []
    )
    mock_analyzer.extract_skills_from_text.assert_not_called()
