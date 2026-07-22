from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


MOCK_CV_DATA = {
    "nombre": "CV Extracted Name",
    "telefono": "809-123-4567",
    "email": "extracted@email.com",
    "habilidades": ["Python", "Machine Learning"],
    "experiencia_anios": 7.5,
    "educacion": "Maestría en Ciencias",
    "resumen": "Extracción exitosa del CV",
    "confianza": 0.95,
}


@patch("app.routers.scanner.upload_file")
@patch("app.routers.scanner.extract_cv_data")
def test_escanear_cv_pdf(mock_extract, mock_upload, client: TestClient):
    mock_upload.return_value = "https://storage.example.com/cv.pdf"
    mock_extract.return_value = MOCK_CV_DATA

    pdf_content = b"%PDF-1.4 fake pdf content"
    response = client.post(
        "/api/escanear/",
        files={"file": ("cv.pdf", pdf_content, "application/pdf")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "CV Extracted Name"
    assert data["email"] == "extracted@email.com"
    assert data["habilidades"] == ["Python", "Machine Learning"]
    assert data["confianza"] == 0.95
    assert data["archivo_url"] == "https://storage.example.com/cv.pdf"

    mock_upload.assert_called_once()
    mock_extract.assert_called_once()


@patch("app.routers.scanner.upload_file")
@patch("app.routers.scanner.extract_cv_data")
def test_escanear_cv_image(mock_extract, mock_upload, client: TestClient):
    mock_upload.return_value = "https://storage.example.com/cv.jpg"
    mock_extract.return_value = MOCK_CV_DATA

    image_content = b"\x89PNG fake image content"
    response = client.post(
        "/api/escanear/",
        files={"file": ("cv.jpg", image_content, "image/jpeg")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "CV Extracted Name"
    assert data["archivo_url"] == "https://storage.example.com/cv.jpg"


def test_escanear_cv_invalid_file_type(client: TestClient):
    txt_content = b"This is not a CV"
    response = client.post(
        "/api/escanear/",
        files={"file": ("cv.txt", txt_content, "text/plain")},
    )

    assert response.status_code == 422
    assert "no permitido" in response.json()["detail"]


def test_escanear_cv_stores_in_database(client: TestClient):
    with (
        patch("app.routers.scanner.upload_file") as mock_upload,
        patch("app.routers.scanner.extract_cv_data") as mock_extract,
    ):
        mock_upload.return_value = "https://storage.example.com/cv.pdf"
        mock_extract.return_value = MOCK_CV_DATA

        pdf_content = b"%PDF-1.4 fake pdf content"
        client.post(
            "/api/escanear/",
            files={"file": ("cv.pdf", pdf_content, "application/pdf")},
        )

        response = client.get("/api/candidatos/")
        assert response.status_code == 200
        candidatos = response.json()
        assert len(candidatos) == 1
        assert candidatos[0]["nombre"] == "CV Extracted Name"
        assert candidatos[0]["datos_crudos"] == MOCK_CV_DATA
