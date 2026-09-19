import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient

MOCK_CV_DATA = {
    "tipo_documento": "CV",
    "tipo_confianza": 0.95,
    "primer_nombre": "cv",
    "primer_apellido": "extracted",
    "datos": {
        "nombre": "CV Extracted Name",
        "telefono": "809-123-4567",
        "email": "extracted@email.com",
        "habilidades": ["Python", "Machine Learning"],
        "experiencia_anios": 7.5,
        "educacion": "Maestría en Ciencias",
        "resumen": "Extracción exitosa del CV",
        "confianza": 0.95,
    },
}


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _auth_headers():
    return {"Authorization": "Bearer fake-token"}


def _mock_data():
    name = _unique("CV Extracted Name")
    data = {**MOCK_CV_DATA, "datos": {**MOCK_CV_DATA["datos"], "nombre": name}}
    return data


@patch("app.routers.scanner.upload_file")
@patch("app.routers.scanner.extract_document_data")
def test_escanear_cv_pdf(mock_extract, mock_upload, client: TestClient, cleanup):
    mock_upload.return_value = "https://storage.example.com/cv.pdf"
    mock_extract.return_value = _mock_data()

    pdf_content = b"%PDF-1.4 fake pdf content"
    response = client.post(
        "/api/escanear/",
        files={"file": ("cv.pdf", pdf_content, "application/pdf")},
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    data = response.json()
    cleanup.table("candidatos", data["id"])
    assert data["email"] == "extracted@email.com"
    assert data["habilidades"] == ["Python", "Machine Learning"]
    assert data["confianza"] == 0.95
    assert data["archivo_url"] == "https://storage.example.com/cv.pdf"

    mock_upload.assert_called_once()
    mock_extract.assert_called_once()


@patch("app.routers.scanner.upload_file")
@patch("app.routers.scanner.extract_document_data")
def test_escanear_cv_image(mock_extract, mock_upload, client: TestClient, cleanup):
    mock_upload.return_value = "https://storage.example.com/cv.jpg"
    mock_extract.return_value = _mock_data()

    image_content = b"\x89PNG fake image content"
    response = client.post(
        "/api/escanear/",
        files={"file": ("cv.jpg", image_content, "image/jpeg")},
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    data = response.json()
    cleanup.table("candidatos", data["id"])
    assert data["archivo_url"] == "https://storage.example.com/cv.jpg"


def test_escanear_cv_invalid_file_type(client: TestClient):
    txt_content = b"This is not a CV"
    response = client.post(
        "/api/escanear/",
        files={"file": ("cv.txt", txt_content, "text/plain")},
        headers=_auth_headers(),
    )

    assert response.status_code == 422
    assert "no permitido" in response.json()["detail"]


@patch("app.routers.scanner.upload_file")
@patch("app.routers.scanner.extract_document_data")
def test_escanear_cv_stores_in_database(
    mock_extract, mock_upload, client: TestClient, cleanup, list_all
):
    mock_upload.return_value = "https://storage.example.com/cv.pdf"
    extracted = _mock_data()
    mock_extract.return_value = extracted

    pdf_content = b"%PDF-1.4 fake pdf content"
    scan = client.post(
        "/api/escanear/",
        files={"file": ("cv.pdf", pdf_content, "application/pdf")},
        headers=_auth_headers(),
    )
    assert scan.status_code == 200
    cleanup.table("candidatos", scan.json()["id"])

    candidatos = list_all(client, "/api/candidatos")
    names = {c["nombre"] for c in candidatos}
    assert extracted["datos"]["nombre"] in names