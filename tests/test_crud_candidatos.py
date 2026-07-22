import uuid

from fastapi.testclient import TestClient


CANDIDATO_DATA = {
    "nombre": "Test User",
    "telefono": "809-555-0000",
    "email": "test@email.com",
    "habilidades": ["Python", "FastAPI"],
    "experiencia_anios": 3.0,
    "educacion": "Ingeniería",
    "resumen": "Test summary",
}


def test_create_candidato(client: TestClient):
    response = client.post("/api/candidatos/", json=CANDIDATO_DATA)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Test User"
    assert data["email"] == "test@email.com"
    assert data["habilidades"] == ["Python", "FastAPI"]
    assert "id" in data
    assert "created_at" in data


def test_list_candidatos(client: TestClient):
    client.post("/api/candidatos/", json=CANDIDATO_DATA)
    client.post("/api/candidatos/", json={**CANDIDATO_DATA, "nombre": "User 2"})

    response = client.get("/api/candidatos/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_candidatos_pagination(client: TestClient):
    for i in range(5):
        client.post("/api/candidatos/", json={**CANDIDATO_DATA, "nombre": f"User {i}"})

    response = client.get("/api/candidatos/?offset=0&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get("/api/candidatos/?offset=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_candidato(client: TestClient):
    create_resp = client.post("/api/candidatos/", json=CANDIDATO_DATA)
    candidato_id = create_resp.json()["id"]

    response = client.get(f"/api/candidatos/{candidato_id}")
    assert response.status_code == 200
    assert response.json()["nombre"] == "Test User"


def test_get_candidato_not_found(client: TestClient):
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/candidatos/{fake_id}")
    assert response.status_code == 404


def test_update_candidato(client: TestClient):
    create_resp = client.post("/api/candidatos/", json=CANDIDATO_DATA)
    candidato_id = create_resp.json()["id"]

    update_data = {"nombre": "Updated Name", "telefono": "809-999-9999"}
    response = client.put(f"/api/candidatos/{candidato_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["nombre"] == "Updated Name"
    assert response.json()["telefono"] == "809-999-9999"
    assert response.json()["email"] == "test@email.com"


def test_delete_candidato(client: TestClient):
    create_resp = client.post("/api/candidatos/", json=CANDIDATO_DATA)
    candidato_id = create_resp.json()["id"]

    response = client.delete(f"/api/candidatos/{candidato_id}")
    assert response.status_code == 204

    get_resp = client.get(f"/api/candidatos/{candidato_id}")
    assert get_resp.status_code == 404


def test_delete_candidato_not_found(client: TestClient):
    fake_id = str(uuid.uuid4())
    response = client.delete(f"/api/candidatos/{fake_id}")
    assert response.status_code == 404
