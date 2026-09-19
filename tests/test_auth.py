import uuid

import pytest
from fastapi.testclient import TestClient


def _email() -> str:
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


def _register(client: TestClient, cleanup, email: str | None = None) -> dict:
    email = email or _email()
    cleanup.auth_email(email)
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "secret123", "full_name": "Nuevo Usuario"},
    )
    assert response.status_code == 200
    return response.json()


@pytest.mark.usefixtures("service_key_ready")
def test_register_creates_pending_user(client: TestClient, cleanup):
    data = _register(client, cleanup)
    assert data["role"] == "user"
    assert data["status"] == "pending"
    assert "manage_users" not in data["permissions"]


@pytest.mark.usefixtures("service_key_ready")
def test_login_rejects_pending_user(client: TestClient, cleanup):
    email = _email()
    _register(client, cleanup, email)

    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "secret123"},
    )
    assert response.status_code == 401
    assert "pendiente" in response.json()["detail"]


@pytest.mark.usefixtures("service_key_ready")
def test_login_approved_user(client: TestClient, cleanup, service_db):
    email = _email()
    data = _register(client, cleanup, email)

    service_db.table("user_profiles").update(
        {"status": "approved", "role": "user"}
    ).eq("id", data["id"]).execute()

    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "secret123"},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["user"]["status"] == "approved"
    assert result["access_token"]


def test_me_returns_logged_user(client: TestClient):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer x"})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"