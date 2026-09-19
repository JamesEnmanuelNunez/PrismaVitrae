import uuid

from fastapi.testclient import TestClient

NO_PROCEDE_DATA = {
    "no": 1,
    "cedula": "001-5555555-5",
    "nombre_completo": "Test No Procede",
    "sexo": "F",
    "cargo_solicitado": "Gerente",
    "salario_solicitado": 70000.0,
    "escolaridad": "Maestría",
}


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _create(client: TestClient, cleanup, **overrides) -> dict:
    data = {**NO_PROCEDE_DATA, **overrides}
    response = client.post("/api/no-proceden/", json=data)
    assert response.status_code == 201
    row = response.json()
    cleanup.table("no_proceden", row["id"])
    return row


def test_create_no_procede(client: TestClient, cleanup):
    data = _create(client, cleanup, nombre_completo=_unique("Test No Procede"))
    assert data["cedula"] == "001-5555555-5"
    assert "id" in data


def test_list_no_proceden(client: TestClient, cleanup, list_all):
    names = [_unique("List No Procede") for _ in range(2)]
    for i, name in enumerate(names):
        _create(client, cleanup, no=i + 1, nombre_completo=name)

    found = {r["nombre_completo"] for r in list_all(client, "/api/no-proceden")}
    assert set(names) <= found


def test_get_no_procede(client: TestClient, cleanup):
    created = _create(client, cleanup, nombre_completo=_unique("Get No Procede"))

    response = client.get(f"/api/no-proceden/{created['id']}")
    assert response.status_code == 200
    assert response.json()["cedula"] == "001-5555555-5"


def test_get_no_procede_not_found(client: TestClient):
    response = client.get(f"/api/no-proceden/{uuid.uuid4()}")
    assert response.status_code == 404


def test_update_no_procede(client: TestClient, cleanup):
    created = _create(client, cleanup, nombre_completo=_unique("Update No Procede"))

    update_data = {"cargo_solicitado": "Gerente General", "observacion": "Actualizado"}
    response = client.put(f"/api/no-proceden/{created['id']}", json=update_data)
    assert response.status_code == 200
    assert response.json()["cargo_solicitado"] == "Gerente General"
    assert response.json()["observacion"] == "Actualizado"


def test_delete_no_procede(client: TestClient, cleanup):
    created = _create(client, cleanup, nombre_completo=_unique("Delete No Procede"))

    response = client.delete(f"/api/no-proceden/{created['id']}")
    assert response.status_code == 204

    get_resp = client.get(f"/api/no-proceden/{created['id']}")
    assert get_resp.status_code == 404