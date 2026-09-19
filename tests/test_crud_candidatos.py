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


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _create(client: TestClient, cleanup, **overrides) -> dict:
    data = {**CANDIDATO_DATA, **overrides}
    response = client.post("/api/candidatos/", json=data)
    assert response.status_code == 201
    row = response.json()
    cleanup.table("candidatos", row["id"])
    return row


def test_create_candidato(client: TestClient, cleanup):
    data = _create(client, cleanup, nombre=_unique("Test User"))
    assert data["email"] == "test@email.com"
    assert data["habilidades"] == ["Python", "FastAPI"]
    assert "id" in data
    assert "created_at" in data


def test_list_candidatos(client: TestClient, cleanup, list_all):
    names = [_unique("List User") for _ in range(2)]
    for name in names:
        _create(client, cleanup, nombre=name)

    found = {c["nombre"] for c in list_all(client, "/api/candidatos")}
    assert set(names) <= found


def test_list_candidatos_pagination(client: TestClient, cleanup, list_all):
    for _ in range(5):
        _create(client, cleanup, nombre=_unique("Page User"))

    first = client.get("/api/candidatos/?offset=0&limit=2")
    second = client.get("/api/candidatos/?offset=2&limit=2")
    assert first.status_code == 200
    assert second.status_code == 200

    first_ids = {c["id"] for c in first.json()}
    second_ids = {c["id"] for c in second.json()}
    assert len(first_ids) <= 2
    assert len(second_ids) <= 2
    assert not (first_ids & second_ids)


def test_get_candidato(client: TestClient, cleanup):
    created = _create(client, cleanup, nombre=_unique("Get User"))

    response = client.get(f"/api/candidatos/{created['id']}")
    assert response.status_code == 200
    assert response.json()["nombre"] == created["nombre"]


def test_get_candidato_not_found(client: TestClient):
    response = client.get(f"/api/candidatos/{uuid.uuid4()}")
    assert response.status_code == 404


def test_update_candidato(client: TestClient, cleanup):
    created = _create(client, cleanup, nombre=_unique("Update User"))
    new_name = _unique("Updated Name")

    response = client.put(
        f"/api/candidatos/{created['id']}", json={"nombre": new_name}
    )
    assert response.status_code == 200
    assert response.json()["nombre"] == new_name
    assert response.json()["email"] == "test@email.com"


def test_delete_candidato(client: TestClient, cleanup):
    created = _create(client, cleanup, nombre=_unique("Delete User"))

    response = client.delete(f"/api/candidatos/{created['id']}")
    assert response.status_code == 204

    get_resp = client.get(f"/api/candidatos/{created['id']}")
    assert get_resp.status_code == 404


def test_delete_candidato_not_found(client: TestClient):
    response = client.delete(f"/api/candidatos/{uuid.uuid4()}")
    assert response.status_code == 404