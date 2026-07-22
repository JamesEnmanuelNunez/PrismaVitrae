import uuid

from fastapi.testclient import TestClient


PROPUESTA_DATA = {
    "no": 1,
    "cedula": "001-1234567-8",
    "nombre_completo": "Test Propuesta",
    "sexo": "M",
    "cargo_solicitado": "Analista",
    "escolaridad": "Universitario",
}


def test_create_propuesta(client: TestClient):
    response = client.post("/api/propuestas/", json=PROPUESTA_DATA)
    assert response.status_code == 201
    data = response.json()
    assert data["cedula"] == "001-1234567-8"
    assert data["nombre_completo"] == "Test Propuesta"
    assert "id" in data


def test_list_propuestas(client: TestClient):
    client.post("/api/propuestas/", json=PROPUESTA_DATA)
    client.post("/api/propuestas/", json={**PROPUESTA_DATA, "no": 2})

    response = client.get("/api/propuestas/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_propuesta(client: TestClient):
    create_resp = client.post("/api/propuestas/", json=PROPUESTA_DATA)
    propuesta_id = create_resp.json()["id"]

    response = client.get(f"/api/propuestas/{propuesta_id}")
    assert response.status_code == 200
    assert response.json()["cedula"] == "001-1234567-8"


def test_get_propuesta_not_found(client: TestClient):
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/propuestas/{fake_id}")
    assert response.status_code == 404


def test_update_propuesta(client: TestClient):
    create_resp = client.post("/api/propuestas/", json=PROPUESTA_DATA)
    propuesta_id = create_resp.json()["id"]

    update_data = {"cargo_aprobado": "Analista Senior", "centro": "Oficina Principal"}
    response = client.put(f"/api/propuestas/{propuesta_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["cargo_aprobado"] == "Analista Senior"
    assert response.json()["centro"] == "Oficina Principal"


def test_delete_propuesta(client: TestClient):
    create_resp = client.post("/api/propuestas/", json=PROPUESTA_DATA)
    propuesta_id = create_resp.json()["id"]

    response = client.delete(f"/api/propuestas/{propuesta_id}")
    assert response.status_code == 204

    get_resp = client.get(f"/api/propuestas/{propuesta_id}")
    assert get_resp.status_code == 404
