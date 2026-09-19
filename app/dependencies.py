from typing import Annotated

from fastapi import Depends, Header
from supabase import Client, create_client

from app.config import settings
from app.exceptions import AuthError, ForbiddenError
from app.schemas.auth import UserResponse
from app.services.auth import get_current_user

_supabase_client: Client | None = None


def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
        )
    return _supabase_client


SupabaseDep = Annotated[Client, Depends(get_supabase)]


def get_token(authorization: str = Header(...)) -> str:
    if not authorization.startswith("Bearer "):
        raise AuthError("Token inválido")
    return authorization.replace("Bearer ", "")


TokenDep = Annotated[str, Depends(get_token)]


def get_current_user_dep(
    db: SupabaseDep,
    token: TokenDep,
) -> UserResponse:
    try:
        return get_current_user(db, token)
    except AuthError:
        raise
    except Exception as exc:
        raise AuthError("No autorizado") from exc


AuthDep = Annotated[UserResponse, Depends(get_current_user_dep)]


def require_permission(permission: str):
    def _check(user: AuthDep) -> UserResponse:
        if permission not in user.permissions:
            raise ForbiddenError(f"Permiso requerido: {permission}")
        return user
    return _check
