from io import BytesIO

from fastapi.testclient import TestClient
from openpyxl import load_workbook


CANDIDATO_DATA = {
    "nombre": "Export Test",
    "telefono": "809-555-0000",
    "email": "export@test.com",
    "habilidades": ["Excel", "Data"],
    "experiencia_anios": 2.0,
    "educacion": "Técnico",
}

PROPUESTA_DATA = {
    "no": 1,
    "cedula": "001-1234567-8",
    "nombre_completo": "Propuesta Export",
    "sexo": "M",
    "cargo_solicitado": "Analista",
}

REAJUSTE_DATA = {
    "cedula": "001-9876543-2",
    "nombre_completo": "Reajuste Export",
    "grupo_ocupacional": "Profesional",
    "cargo": "Ingeniero",
    "salario_actual": 35000.0,
    "salario_solicitado": 42000.0,
}

NO_PROCEDER_DATA = {
    "no": 1,
    "cedula": "001-5555555-5",
    "nombre_completo": "No Proceder Export",
    "sexo": "F",
    "cargo_solicitado": "Gerente",
    "salario_solicitado": 70000.0,
    "escolaridad": "Maestría",
}


def test_export_candidatos_empty(client: TestClient):
    response = client.get("/api/exportar-excel/candidatos")
    assert response.status_code == 200
    assert "spreadsheetml" in response.headers["content-type"]

    wb = load_workbook(BytesIO(response.content))
    ws = wb.active
    assert ws.title == "Candidatos"
    assert ws.max_row == 1


def test_export_candidatos_with_data(client: TestClient):
    client.post("/api/candidatos/", json=CANDIDATO_DATA)
    client.post("/api/candidatos/", json={**CANDIDATO_DATA, "nombre": "Export Test 2"})

    response = client.get("/api/exportar-excel/candidatos")
    assert response.status_code == 200

    wb = load_workbook(BytesIO(response.content))
    ws = wb.active
    assert ws.max_row == 3
    assert ws.cell(row=2, column=2).value == "Export Test"


def test_export_propuestas(client: TestClient):
    client.post("/api/propuestas/", json=PROPUESTA_DATA)

    response = client.get("/api/exportar-excel/propuestas")
    assert response.status_code == 200

    wb = load_workbook(BytesIO(response.content))
    ws = wb.active
    assert ws.title == "Propuestas"
    assert ws.max_row == 2
    assert ws.cell(row=2, column=4).value == "Propuesta Export"


def test_export_reajustes(client: TestClient):
    client.post("/api/reajustes/", json=REAJUSTE_DATA)

    response = client.get("/api/exportar-excel/reajustes")
    assert response.status_code == 200

    wb = load_workbook(BytesIO(response.content))
    ws = wb.active
    assert ws.title == "Reajustes"
    assert ws.max_row == 2
    assert ws.cell(row=2, column=5).value == 35000.0


def test_export_no_proceden(client: TestClient):
    client.post("/api/no-proceden/", json=NO_PROCEDER_DATA)

    response = client.get("/api/exportar-excel/no_proceden")
    assert response.status_code == 200

    wb = load_workbook(BytesIO(response.content))
    ws = wb.active
    assert ws.title == "No Proceden"
    assert ws.max_row == 2


def test_export_invalid_table(client: TestClient):
    response = client.get("/api/exportar-excel/tabla_inexistente")
    assert response.status_code == 404
    assert "no encontrada" in response.json()["detail"]
