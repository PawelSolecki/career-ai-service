import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.offer_routes import router
from app.model.job_offer import JobOffer
from app.model.skill_result import SkillResult, SkillItem


test_app = FastAPI()
test_app.include_router(router, prefix="/api/v1/offer")

client = TestClient(test_app)


@pytest.fixture
def mock_offer_analyzer(monkeypatch):
    mock = MagicMock()
    mock.analyze_job_offer.return_value = SkillResult(
        hard_skills=[SkillItem(name="Python", score=0.9)],
        soft_skills=[SkillItem(name="Communication", score=0.8)],
        tools=[SkillItem(name="Docker", score=0.7)],
    )
    monkeypatch.setattr("app.api.offer_routes.offer_analyzer", mock)
    return mock


@pytest.fixture
def sample_job_offer():
    return {
        "description": "We are looking for a skilled Python developer",
        "technologies": ["Python", "Django", "PostgreSQL"],
        "requirements": ["3+ years experience", "Strong communication skills"],
        "responsibilities": ["Develop web applications", "Work with team"],
    }


def test_analyze_job_offer_success(mock_offer_analyzer, sample_job_offer):
    response = client.post("/api/v1/offer/analyze-offer", json=sample_job_offer)

    assert response.status_code == 200
    data = response.json()

    assert "hard_skills" in data
    assert "soft_skills" in data
    assert "tools" in data

    assert len(data["hard_skills"]) == 1
    assert data["hard_skills"][0]["name"] == "Python"
    assert data["hard_skills"][0]["score"] == 0.9

    assert len(data["soft_skills"]) == 1
    assert data["soft_skills"][0]["name"] == "Communication"
    assert data["soft_skills"][0]["score"] == 0.8

    assert len(data["tools"]) == 1
    assert data["tools"][0]["name"] == "Docker"
    assert data["tools"][0]["score"] == 0.7

    mock_offer_analyzer.analyze_job_offer.assert_called_once()
    call_args = mock_offer_analyzer.analyze_job_offer.call_args

    job_data = call_args[0][0]
    assert job_data["description"] == sample_job_offer["description"]
    assert job_data["technologies"] == sample_job_offer["technologies"]
    assert job_data["requirements"] == sample_job_offer["requirements"]
    assert job_data["responsibilities"] == sample_job_offer["responsibilities"]


def test_analyze_job_offer_with_max_results_parameter(
    mock_offer_analyzer, sample_job_offer
):
    response = client.post(
        "/api/v1/offer/analyze-offer?max_results_per_category=5", json=sample_job_offer
    )

    assert response.status_code == 200

    mock_offer_analyzer.analyze_job_offer.assert_called_once()
    call_args = mock_offer_analyzer.analyze_job_offer.call_args
    call_kwargs = call_args[1]
    assert "max_results_per_category" in call_kwargs
    assert call_kwargs["max_results_per_category"] == 5


def test_analyze_job_offer_minimal_data(mock_offer_analyzer):
    minimal_offer = {"description": "Basic job description"}

    response = client.post("/api/v1/offer/analyze-offer", json=minimal_offer)

    assert response.status_code == 200
    mock_offer_analyzer.analyze_job_offer.assert_called_once()


def test_analyze_job_offer_empty_data(mock_offer_analyzer):
    empty_offer = {}

    response = client.post("/api/v1/offer/analyze-offer", json=empty_offer)

    assert response.status_code == 200
    mock_offer_analyzer.analyze_job_offer.assert_called_once()


def test_analyze_job_offer_null_fields(mock_offer_analyzer):
    offer_with_nulls = {
        "description": None,
        "technologies": None,
        "requirements": ["Some requirement"],
        "responsibilities": None,
    }

    response = client.post("/api/v1/offer/analyze-offer", json=offer_with_nulls)

    assert response.status_code == 200
    mock_offer_analyzer.analyze_job_offer.assert_called_once()


def test_analyze_job_offer_internal_error(monkeypatch, sample_job_offer):
    def broken_analyze_job_offer(*args, **kwargs):
        raise RuntimeError("Analysis failed")

    monkeypatch.setattr(
        "app.api.offer_routes.offer_analyzer.analyze_job_offer",
        broken_analyze_job_offer,
    )

    response = client.post("/api/v1/offer/analyze-offer", json=sample_job_offer)

    assert response.status_code == 500
    assert "Error analyzing job offer" in response.json()["detail"]


def test_analyze_job_offer_invalid_json():
    response = client.post(
        "/api/v1/offer/analyze-offer",
        data="invalid json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422


def test_analyze_job_offer_invalid_field_types(mock_offer_analyzer):
    invalid_offer = {
        "description": "Valid description",
        "technologies": "Should be a list, not string",
        "requirements": ["Valid requirement"],
        "responsibilities": 123,
    }

    response = client.post("/api/v1/offer/analyze-offer", json=invalid_offer)

    assert response.status_code == 422


def test_analyze_job_offer_with_lists(mock_offer_analyzer):
    offer_with_lists = {
        "description": "Job with detailed lists",
        "technologies": ["Python", "React", "PostgreSQL"],
        "requirements": [
            "Bachelor's degree in Computer Science",
            "3+ years of experience",
            "Knowledge of web frameworks",
        ],
        "responsibilities": [
            "Design and implement software solutions",
            "Collaborate with cross-functional teams",
            "Maintain code quality",
        ],
    }

    response = client.post("/api/v1/offer/analyze-offer", json=offer_with_lists)

    assert response.status_code == 200

    mock_offer_analyzer.analyze_job_offer.assert_called_once()
    call_args = mock_offer_analyzer.analyze_job_offer.call_args
    job_data = call_args[0][0]

    assert job_data["technologies"] == offer_with_lists["technologies"]
    assert job_data["requirements"] == offer_with_lists["requirements"]
    assert job_data["responsibilities"] == offer_with_lists["responsibilities"]


def test_job_offer_model_to_dict():
    job_offer = JobOffer(
        description="Test description",
        technologies=["Python", "Django"],
        requirements=["3+ years experience"],
        responsibilities=["Develop applications"],
    )

    result = job_offer.to_dict()

    assert result["description"] == "Test description"
    assert result["technologies"] == ["Python", "Django"]
    assert result["requirements"] == ["3+ years experience"]
    assert result["responsibilities"] == ["Develop applications"]


def test_job_offer_model_with_none_values():
    job_offer = JobOffer(
        description="Test description",
        technologies=None,
        requirements=None,
        responsibilities=None,
    )

    result = job_offer.to_dict()

    assert result["description"] == "Test description"
    assert result["technologies"] is None
    assert result["requirements"] is None
    assert result["responsibilities"] is None
