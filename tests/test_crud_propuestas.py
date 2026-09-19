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


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _create(client: TestClient, cleanup, **overrides) -> dict:
    data = {**PROPUESTA_DATA, **overrides}
    response = client.post("/api/propuestas/", json=data)
    assert response.status_code == 201
    row = response.json()
    cleanup.table("propuestas", row["id"])
    return row


def test_create_propuesta(client: TestClient, cleanup):
    data = _create(client, cleanup, nombre_completo=_unique("Test Propuesta"))
    assert data["cedula"] == "001-1234567-8"
    assert "id" in data


def test_list_propuestas(client: TestClient, cleanup, list_all):
    names = [_unique("List Propuesta") for _ in range(2)]
    for i, name in enumerate(names):
        _create(client, cleanup, no=i + 1, nombre_completo=name)

    found = {p["nombre_completo"] for p in list_all(client, "/api/propuestas")}
    assert set(names) <= found


def test_get_propuesta(client: TestClient, cleanup):
    created = _create(client, cleanup, nombre_completo=_unique("Get Propuesta"))

    response = client.get(f"/api/propuestas/{created['id']}")
    assert response.status_code == 200
    assert response.json()["cedula"] == "001-1234567-8"


def test_get_propuesta_not_found(client: TestClient):
    response = client.get(f"/api/propuestas/{uuid.uuid4()}")
    assert response.status_code == 404


def test_update_propuesta(client: TestClient, cleanup):
    created = _create(client, cleanup, nombre_completo=_unique("Update Propuesta"))

    update_data = {"cargo_aprobado": "Analista Senior", "centro": "Oficina Principal"}
    response = client.put(f"/api/propuestas/{created['id']}", json=update_data)
    assert response.status_code == 200
    assert response.json()["cargo_aprobado"] == "Analista Senior"
    assert response.json()["centro"] == "Oficina Principal"


def test_delete_propuesta(client: TestClient, cleanup):
    created = _create(client, cleanup, nombre_completo=_unique("Delete Propuesta"))

    response = client.delete(f"/api/propuestas/{created['id']}")
    assert response.status_code == 204

    get_resp = client.get(f"/api/propuestas/{created['id']}")
    assert get_resp.status_code == 404