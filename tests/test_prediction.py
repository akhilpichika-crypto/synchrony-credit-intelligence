
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def get_auth_headers():
    response = client.post(
        "/auth/login",
        json={
            "email": "analyst@demo.com",
            "password": "Analyst@123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


VALID_APPLICANT = {
    "age": 42,
    "annual_income": 744000,
    "requested_loan_amount": 150000,
    "home_ownership": "OWN",
    "employment_duration": 8,
    "loan_intent": "PERSONAL",
    "duration_months": 12,
}

def test_valid_prediction():
    response = client.post(
        "/predict",
        json=VALID_APPLICANT,
        headers=get_auth_headers(),
    )

    assert response.status_code == 200

    data = response.json()

    assert "risk_probability" in data
    assert "risk_percentage" in data
    assert "risk_level" in data
    assert "top_factors" in data

    assert 0 <= data["risk_probability"] <= 1
    assert 0 <= data["risk_percentage"] <= 100

    assert data["risk_level"] in {
        "LOW",
        "MEDIUM",
        "HIGH",
    }

    assert isinstance(data["top_factors"], list)
    assert len(data["top_factors"]) > 0


def test_invalid_applicant_age():
    invalid_applicant = VALID_APPLICANT.copy()
    invalid_applicant["age"] = 10

    response = client.post(
        "/predict",
        json=invalid_applicant,
        headers=get_auth_headers(),
    )

    assert response.status_code == 422


def test_missing_required_field():
    invalid_applicant = VALID_APPLICANT.copy()
    del invalid_applicant["requested_loan_amount"]

    response = client.post(
        "/predict",
        json=invalid_applicant,
        headers=get_auth_headers(),
    )

    assert response.status_code == 422