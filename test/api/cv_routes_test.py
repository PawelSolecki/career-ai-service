import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.cv_routes import router
from app.model.user_cv import UserCV

# Create a test app with just the CV router
test_app = FastAPI()
test_app.include_router(router, prefix="/api/v1/cv")

client = TestClient(test_app)


@pytest.fixture
def mock_cv_service(monkeypatch):
    mock = MagicMock()
    mock.analyze_cv.return_value = UserCV(
        personal_info=UserCV.PersonalInfo(first_name="Jan", last_name="Kowalski"),
        experience=[],
    )
    monkeypatch.setattr("app.api.cv_routes.cv_service", mock)
    return mock


def test_analyze_cv_success(mock_cv_service):
    payload = {
        "personal_info": {"first_name": "Jan", "last_name": "Kowalski"},
        "experience": [],
    }

    response = client.post(
        "/api/v1/cv/analyze-cv?alpha=1.0&top_k=5&min_score=0.1", json=payload
    )

    assert response.status_code == 200
    data = response.json()
    assert data["personal_info"]["first_name"] == "Jan"
    assert data["personal_info"]["last_name"] == "Kowalski"

    mock_cv_service.analyze_cv.assert_called_once()


def test_analyze_cv_internal_error(monkeypatch):
    def broken_analyze_cv(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("app.api.cv_routes.cv_service.analyze_cv", broken_analyze_cv)

    payload = {
        "personal_info": {"first_name": "Jan", "last_name": "Kowalski"},
        "experience": [],
    }

    response = client.post("/api/v1/cv/analyze-cv", json=payload)

    assert response.status_code == 500
    assert response.json()["detail"].startswith("Error analyzing CV")


def test_generate_bio_success(mock_cv_service):
    # Test data
    payload = {
        "user_cv": {
            "personal_info": {
                "first_name": "Jan",
                "last_name": "Kowalski",
                "role": "Senior Python Developer",
                "summary": "Experienced Python developer",
            },
            "experience": [
                {
                    "position": "Senior Developer",
                    "company": "Tech Corp",
                    "summaries": [
                        {
                            "text": "Led development team",
                            "technologies": ["Python", "Django"],
                        }
                    ],
                }
            ],
            "skills": ["Python", "Django", "FastAPI"],
            "projects": [
                {
                    "name": "API Project",
                    "summaries": [
                        {
                            "text": "Developed REST API",
                            "technologies": ["FastAPI", "Python"],
                        }
                    ],
                }
            ],
        },
        "skill_result": {
            "hard_skills": [{"name": "Python", "score": 0.9}],
            "soft_skills": [{"name": "Communication", "score": 0.8}],
            "tools": [{"name": "Git", "score": 0.7}],
        },
        "job_offer": {
            "description": "Python Developer position",
            "technologies": ["Python", "Django"],
            "requirements": ["5+ years experience"],
            "responsibilities": ["Develop web applications"],
        },
    }

    # Mock the service response
    mock_cv_service.generate_bio.return_value = "Generated bio text"

    response = client.post("/api/v1/cv/generate-bio", json=payload)

    assert response.status_code == 200
    assert response.json() == {"bio": "Generated bio text"}
    mock_cv_service.generate_bio.assert_called_once()


def test_generate_bio_internal_error(monkeypatch):
    def broken_generate_bio(*args, **kwargs):
        raise RuntimeError("Bio generation failed")

    monkeypatch.setattr(
        "app.api.cv_routes.cv_service.generate_bio", broken_generate_bio
    )

    # Minimal valid payload
    payload = {
        "user_cv": {"personal_info": {"first_name": "Jan", "last_name": "Kowalski"}},
        "skill_result": {"hard_skills": [], "soft_skills": [], "tools": []},
        "job_offer": {
            "description": "Test",
            "technologies": [],
            "requirements": [],
            "responsibilities": [],
        },
    }

    response = client.post("/api/v1/cv/generate-bio", json=payload)

    assert response.status_code == 500
    assert "Error generating bio" in response.json()["detail"]
