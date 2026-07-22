import uuid

from fastapi.testclient import TestClient


NO_PROCEDER_DATA = {
    "no": 1,
    "cedula": "001-5555555-5",
    "nombre_completo": "Test No Proceder",
    "sexo": "F",
    "cargo_solicitado": "Gerente",
    "salario_solicitado": 80000.0,
    "escolaridad": "Maestría",
    "observacion": "No cumple requisitos",
}


def test_create_no_procede(client: TestClient):
    response = client.post("/api/no-proceden/", json=NO_PROCEDER_DATA)
    assert response.status_code == 201
    data = response.json()
    assert data["cedula"] == "001-5555555-5"
    assert data["salario_solicitado"] == 80000.0
    assert "id" in data


def test_list_no_proceden(client: TestClient):
    client.post("/api/no-proceden/", json=NO_PROCEDER_DATA)
    client.post("/api/no-proceden/", json={**NO_PROCEDER_DATA, "no": 2})

    response = client.get("/api/no-proceden/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_no_procede(client: TestClient):
    create_resp = client.post("/api/no-proceden/", json=NO_PROCEDER_DATA)
    no_procede_id = create_resp.json()["id"]

    response = client.get(f"/api/no-proceden/{no_procede_id}")
    assert response.status_code == 200
    assert response.json()["nombre_completo"] == "Test No Proceder"


def test_get_no_procede_not_found(client: TestClient):
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/no-proceden/{fake_id}")
    assert response.status_code == 404


def test_update_no_procede(client: TestClient):
    create_resp = client.post("/api/no-proceden/", json=NO_PROCEDER_DATA)
    no_procede_id = create_resp.json()["id"]

    update_data = {"observacion": "Actualizado - ahora procede"}
    response = client.put(f"/api/no-proceden/{no_procede_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["observacion"] == "Actualizado - ahora procede"


def test_delete_no_procede(client: TestClient):
    create_resp = client.post("/api/no-proceden/", json=NO_PROCEDER_DATA)
    no_procede_id = create_resp.json()["id"]

    response = client.delete(f"/api/no-proceden/{no_procede_id}")
    assert response.status_code == 204

    get_resp = client.get(f"/api/no-proceden/{no_procede_id}")
    assert get_resp.status_code == 404
