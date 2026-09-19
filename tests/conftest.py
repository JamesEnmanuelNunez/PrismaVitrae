from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from supabase import create_client

from app.config import settings
from app.dependencies import get_token
from app.main import app
from app.schemas.auth import UserResponse
from app.services.auth import DEFAULT_PERMISSIONS

MOCK_USER = UserResponse(
    id="test-user-id",
    email="test@example.com",
    role="admin",
    status="approved",
    permissions=DEFAULT_PERMISSIONS["admin"],
)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def service_db():
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


def _service_key_valid() -> bool:
    try:
        db = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        db.auth.admin.list_users()
        return True
    except Exception:
        return False


@pytest.fixture
def service_key_ready():
    """Requiere una service role key real en SUPABASE_SERVICE_KEY.

    Los tests de auth registran/borran usuarios reales en Auth de Supabase;
    sin la service key no pueden aprobarse ni limpiarse.
    """
    if not _service_key_valid():
        pytest.skip(
            "SUPABASE_SERVICE_KEY no es una service role key válida en .env"
        )
    return True


@pytest.fixture
def list_all():
    """Itera la paginación (máx 100 por página) y devuelve todas las filas."""

    def _list_all(client, path: str, limit: int = 100) -> list[dict]:
        rows = []
        offset = 0
        while True:
            response = client.get(f"{path}?offset={offset}&limit={limit}")
            assert response.status_code == 200, response.text
            page = response.json()
            rows.extend(page)
            if len(page) < limit:
                return rows
            offset += limit

    return _list_all


class CleanupTracker:
    """Elimina tras cada test los datos creados contra el Supabase real."""

    def __init__(self, db):
        self._db = db
        self._items = []

    def table(self, table: str, item_id: str) -> str:
        self._items.append(("table", table, item_id))
        return item_id

    def auth_email(self, email: str) -> str:
        self._items.append(("auth_email", email))
        return email

    def run(self) -> None:
        failures = 0
        for entry in reversed(self._items):
            try:
                if entry[0] == "table":
                    self._db.table(entry[1]).delete().eq("id", entry[2]).execute()
                else:
                    users = getattr(self._db.auth.admin.list_users(), "users", []) or []
                    for user in users:
                        if getattr(user, "email", None) == entry[1]:
                            self._db.auth.admin.delete_user(user.id)
                            break
            except Exception:
                failures += 1
        if failures:
            print(f"[cleanup] {failures} limpiezas fallaron (revisar manualmente)")


@pytest.fixture
def cleanup() -> CleanupTracker:
    tracker = CleanupTracker(
        create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    )
    yield tracker
    tracker.run()


@pytest.fixture(autouse=True)
def mock_auth():
    app.dependency_overrides[get_token] = lambda: "fake-token"
    with patch("app.dependencies.get_current_user", return_value=MOCK_USER):
        yield
    app.dependency_overrides.pop(get_token, None)