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
