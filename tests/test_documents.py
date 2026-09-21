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


def test_valid_pdf_document():
    pdf_path = TEST_DIR / "government_employee_financial.pdf"

    with open(pdf_path, "rb") as file:
        response = client.post(
            "/documents/index",
            files={
                "file": (
                    "government_employee_financial.pdf",
                    file,
                    "application/pdf",
                )
            },
            headers=get_auth_headers(),
        )

    assert response.status_code == 200

    data = response.json()
	
    assert "filename" in data
    assert "page_count" in data
    assert "chunks_stored" in data

    assert data["filename"] == "government_employee_financial.pdf"
    assert data["page_count"] > 0
    assert data["chunks_stored"] > 0


def test_document_endpoint_without_token():
    pdf_path = TEST_DIR / "government_employee_financial.pdf"

    with open(pdf_path, "rb") as file:
        response = client.post(
            "/documents/index",
            files={
                "file": (
                    "government_employee_financial.pdf",
                    file,
                    "application/pdf",
                )
            },
        )

    assert response.status_code in (401, 403)


def test_invalid_document_file_type():
    response = client.post(
        "/documents/index",
        files={
            "file": (
                "financial_document.txt",
                b"This is not a PDF.",
                "text/plain",
            )
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 400


def test_corrupted_pdf():
    fake_pdf = (
        b"%PDF-1.4\n"
        b"This has a PDF signature but is not a valid PDF file."
    )

    response = client.post(
        "/documents/index",
        files={
            "file": (
                "corrupted.pdf",
                fake_pdf,
                "application/pdf",
            )
        },
        headers=get_auth_headers(),
    )

    assert response.status_code == 400