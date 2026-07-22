import uuid

from fastapi.testclient import TestClient


REAJUSTE_DATA = {
    "cedula": "001-9876543-2",
    "nombre_completo": "Test Reajuste",
    "grupo_ocupacional": "Profesional",
    "cargo": "Ingeniero",
    "salario_actual": 40000.0,
    "salario_solicitado": 50000.0,
}


def test_create_reajuste(client: TestClient):
    response = client.post("/api/reajustes/", json=REAJUSTE_DATA)
    assert response.status_code == 201
    data = response.json()
    assert data["cedula"] == "001-9876543-2"
    assert data["salario_actual"] == 40000.0
    assert data["salario_solicitado"] == 50000.0
    assert "id" in data


def test_list_reajustes(client: TestClient):
    client.post("/api/reajustes/", json=REAJUSTE_DATA)
    client.post("/api/reajustes/", json={**REAJUSTE_DATA, "cedula": "001-1111111-1"})

    response = client.get("/api/reajustes/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_reajuste(client: TestClient):
    create_resp = client.post("/api/reajustes/", json=REAJUSTE_DATA)
    reajuste_id = create_resp.json()["id"]

    response = client.get(f"/api/reajustes/{reajuste_id}")
    assert response.status_code == 200
    assert response.json()["nombre_completo"] == "Test Reajuste"


def test_get_reajuste_not_found(client: TestClient):
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/reajustes/{fake_id}")
    assert response.status_code == 404


def test_update_reajuste(client: TestClient):
    create_resp = client.post("/api/reajustes/", json=REAJUSTE_DATA)
    reajuste_id = create_resp.json()["id"]

    update_data = {"salario_solicitado": 55000.0, "observacion": "Aprobado por gerencia"}
    response = client.put(f"/api/reajustes/{reajuste_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["salario_solicitado"] == 55000.0
    assert response.json()["observacion"] == "Aprobado por gerencia"


def test_delete_reajuste(client: TestClient):
    create_resp = client.post("/api/reajustes/", json=REAJUSTE_DATA)
    reajuste_id = create_resp.json()["id"]

    response = client.delete(f"/api/reajustes/{reajuste_id}")
    assert response.status_code == 204

    get_resp = client.get(f"/api/reajustes/{reajuste_id}")
    assert get_resp.status_code == 404
