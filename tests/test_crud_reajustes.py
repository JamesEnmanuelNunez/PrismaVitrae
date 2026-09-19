import uuid

from fastapi.testclient import TestClient

REAJUSTE_DATA = {
    "cedula": "001-9876543-2",
    "nombre_completo": "Test Reajuste",
    "grupo_ocupacional": "Profesional",
    "cargo": "Ingeniero",
    "salario_actual": 35000.0,
    "salario_solicitado": 42000.0,
}


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _create(client: TestClient, cleanup, **overrides) -> dict:
    data = {**REAJUSTE_DATA, **overrides}
    response = client.post("/api/reajustes/", json=data)
    assert response.status_code == 201
    row = response.json()
    cleanup.table("reajustes", row["id"])
    return row


def test_create_reajuste(client: TestClient, cleanup):
    data = _create(client, cleanup, nombre_completo=_unique("Test Reajuste"))
    assert data["cedula"] == "001-9876543-2"
    assert "id" in data


def test_list_reajustes(client: TestClient, cleanup, list_all):
    names = [_unique("List Reajuste") for _ in range(2)]
    for name in names:
        _create(client, cleanup, nombre_completo=name)

    found = {r["nombre_completo"] for r in list_all(client, "/api/reajustes")}
    assert set(names) <= found


def test_get_reajuste(client: TestClient, cleanup):
    created = _create(client, cleanup, nombre_completo=_unique("Get Reajuste"))

    response = client.get(f"/api/reajustes/{created['id']}")
    assert response.status_code == 200
    assert response.json()["cedula"] == "001-9876543-2"


def test_get_reajuste_not_found(client: TestClient):
    response = client.get(f"/api/reajustes/{uuid.uuid4()}")
    assert response.status_code == 404


def test_update_reajuste(client: TestClient, cleanup):
    created = _create(client, cleanup, nombre_completo=_unique("Update Reajuste"))

    update_data = {
        "salario_solicitado": 55000.0,
        "observacion": "Aprobado por gerencia",
    }
    response = client.put(f"/api/reajustes/{created['id']}", json=update_data)
    assert response.status_code == 200
    assert response.json()["salario_solicitado"] == 55000.0
    assert response.json()["observacion"] == "Aprobado por gerencia"


def test_delete_reajuste(client: TestClient, cleanup):
    created = _create(client, cleanup, nombre_completo=_unique("Delete Reajuste"))

    response = client.delete(f"/api/reajustes/{created['id']}")
    assert response.status_code == 204

    get_resp = client.get(f"/api/reajustes/{created['id']}")
    assert get_resp.status_code == 404