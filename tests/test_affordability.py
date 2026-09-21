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


def test_valid_affordability_analysis():
    payload = {
        "stable_monthly_income": 62000,
        "observed_monthly_expenses": 35150,
        "city": "Hyderabad",
        "existing_monthly_obligations": 0,
        "risk_band": "LOW",
        "duration_months": 12,
    }

    response = client.post(
        "/affordability/analyze",
        json=payload,
        headers=get_auth_headers(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["stable_monthly_income"] == 62000
    assert data["living_expense_used"] == 35150
    assert data["repayment_surplus"] == 26850
    assert data["affordable_emi"] == 16110
    assert data["safety_buffer"] == 10740
    assert data["estimated_apr"] == 10.0
    assert data["duration_months"] == 12

    assert data["indicative_loan_capacity"] > 0


def test_no_repayment_surplus():
    payload = {
        "stable_monthly_income": 20000,
        "observed_monthly_expenses": 25000,
        "city": "Hyderabad",
        "existing_monthly_obligations": 0,
        "risk_band": "HIGH",
        "duration_months": 12,
    }

    response = client.post(
        "/affordability/analyze",
        json=payload,
        headers=get_auth_headers(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["repayment_surplus"] <= 0
    assert data["affordable_emi"] == 0
    assert data["safety_buffer"] == 0
    assert data["indicative_loan_capacity"] == 0


def test_city_reference_is_used():
    payload = {
        "stable_monthly_income": 50000,
        "observed_monthly_expenses": 15000,
        "city": "Mumbai",
        "existing_monthly_obligations": 0,
        "risk_band": "MEDIUM",
        "duration_months": 18,
    }

    response = client.post(
        "/affordability/analyze",
        json=payload,
        headers=get_auth_headers(),
    )

    assert response.status_code == 200

    data = response.json()

    # Mumbai prototype living-cost reference = ₹30,000,
    # which is higher than the observed ₹15,000.
    assert data["living_expense_used"] == 30000
    assert data["repayment_surplus"] == 20000
    assert data["affordable_emi"] == 12000
    assert data["safety_buffer"] == 8000
    assert data["estimated_apr"] == 14.0


def test_affordability_without_token():
    payload = {
        "stable_monthly_income": 62000,
        "observed_monthly_expenses": 35150,
        "city": "Hyderabad",
        "existing_monthly_obligations": 0,
        "risk_band": "LOW",
        "duration_months": 12,
    }

    response = client.post(
        "/affordability/analyze",
        json=payload,
    )

    assert response.status_code in (401, 403)