import pytest
from app.service.cv_service import CVService
from datetime import date
import json
from unittest.mock import MagicMock, mock_open, patch
from app.model.job_offer import JobOffer
from app.model.skill_result import SkillResult, SkillItem
from app.model.user_cv import UserCV


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
def sample_bio_inputs():
    user_cv = UserCV(
        personal_info=UserCV.PersonalInfo(
            first_name="Jan", last_name="Kowalski", summary="Senior Python Developer"
        ),
        skills=["Python", "Django", "FastAPI"],  # List of strings, not complex objects
        experience=[
            UserCV.Experience(
                position="Senior Developer",
                company="Tech Corp",
                start_date=date(2020, 1, 1),
                end_date=date(2023, 12, 31),
                summaries=[
                    UserCV.Summary(
                        text="Led development team", technologies=["Python", "Django"]
                    )
                ],
            )
        ],
    )

    skill_result = SkillResult(
        hard_skills=[SkillItem(name="Python", score=0.9)],
        soft_skills=[SkillItem(name="Communication", score=0.8)],
        tools=[SkillItem(name="Git", score=0.7)],
    )

    job_offer = JobOffer(
        description="Python Developer position",
        technologies=["Python", "Django"],
        requirements=["5+ years experience"],
        responsibilities=["Develop web applications"],
    )

    return user_cv, skill_result, job_offer


@pytest.fixture
def mock_requests(monkeypatch):
    mock = MagicMock()
    mock.post.return_value.json.return_value = {"response": "Generated bio text"}
    mock.post.return_value.raise_for_status = MagicMock()
    monkeypatch.setattr("app.service.cv_service.requests", mock)
    return mock


def test_generate_bio_success(sample_bio_inputs, mock_requests):
    user_cv, skill_result, job_offer = sample_bio_inputs
    service = CVService()

    with patch("builtins.open", mock_open(read_data='{"instructions": "Write a bio"}')):
        bio = service.generate_bio(user_cv, skill_result, job_offer)

        assert bio == "Generated bio text"
        mock_requests.post.assert_called_once()


def test_generate_bio_file_error(sample_bio_inputs):
    user_cv, skill_result, job_offer = sample_bio_inputs
    service = CVService()

    with (
        patch("builtins.open", side_effect=FileNotFoundError),
        pytest.raises(FileNotFoundError),
    ):
        service.generate_bio(user_cv, skill_result, job_offer)


def test_generate_bio_api_error(sample_bio_inputs, mock_requests):
    user_cv, skill_result, job_offer = sample_bio_inputs
    service = CVService()

    # Simulate API error
    mock_requests.post.side_effect = Exception("API Error")

    with (
        patch("builtins.open", mock_open(read_data='{"instructions": "Write a bio"}')),
        pytest.raises(Exception, match="API Error"),
    ):
        service.generate_bio(user_cv, skill_result, job_offer)


def test_generate_bio_empty_response(sample_bio_inputs, mock_requests):
    user_cv, skill_result, job_offer = sample_bio_inputs
    service = CVService()

    # Simulate empty response
    mock_requests.post.return_value.json.return_value = {}

    with patch("builtins.open", mock_open(read_data='{"instructions": "Write a bio"}')):
        bio = service.generate_bio(user_cv, skill_result, job_offer)
        assert bio == ""


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
