from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)

TEST_DIR = Path(__file__).parent


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


def test_valid_transaction_analysis():
    csv_path = TEST_DIR / "government_employee_transactions.csv"

    with open(csv_path, "rb") as file:
        response = client.post(
            "/behavior/analyze",
            files={
                "file": (
                    "government_employee_transactions.csv",
                    file,
                    "text/csv",
                )
            },
            headers=get_auth_headers(),
        )

    assert response.status_code == 200

    data = response.json()

    assert "income_stability" in data
    assert "cashflow_consistency" in data
    assert "spending_volatility" in data
    assert "spending_volatility_score" in data
    assert "average_savings_rate" in data
    assert "stable_monthly_income" in data
    assert "observed_monthly_expenses" in data
    assert "months_analyzed" in data
    assert "total_transactions" in data

    assert 0 <= data["income_stability"] <= 100
    assert 0 <= data["cashflow_consistency"] <= 100
    assert data["months_analyzed"] > 0
    assert data["total_transactions"] > 0


def test_behavioral_endpoint_without_token():
    csv_path = TEST_DIR / "government_employee_transactions.csv"

    with open(csv_path, "rb") as file:
        response = client.post(
            "/behavior/analyze",
            files={
                "file": (
                    "government_employee_transactions.csv",
                    file,
                    "text/csv",
                )
            },
        )

    assert response.status_code in (401, 403)


def test_invalid_file_type():
    response = client.post(
        "/behavior/analyze",
        files={
            "file": (
                "transactions.txt",
                b"this is not a csv transaction statement",
                "text/plain",
            )
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 400


def test_invalid_csv_schema():
    invalid_csv = (
        b"name,value\n"
        b"example,100\n"
    )

    response = client.post(
        "/behavior/analyze",
        files={
            "file": (
                "invalid_transactions.csv",
                invalid_csv,
                "text/csv",
            )
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 400