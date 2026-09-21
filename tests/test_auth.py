from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_valid_login():
    response = client.post(
        "/auth/login",
        json={
            "email": "analyst@demo.com",
            "password": "Analyst@123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_invalid_password():
    response = client.post(
        "/auth/login",
        json={
            "email": "analyst@demo.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_invalid_user():
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "anything",
        },
    )

    assert response.status_code == 401


def test_protected_predict_without_token():
    response = client.post(
        "/predict",
        json={},
    )

    assert response.status_code in (401, 403)