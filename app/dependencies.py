from typing import Annotated

from fastapi import Depends, Header, HTTPException
from supabase import Client, create_client

from app.config import settings
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
        raise HTTPException(status_code=401, detail="Token inválido")
    return authorization.replace("Bearer ", "")


TokenDep = Annotated[str, Depends(get_token)]


def get_current_user_dep(
    db: SupabaseDep,
    token: TokenDep,
) -> UserResponse:
    try:
        return get_current_user(db, token)
    except Exception:
        raise HTTPException(status_code=401, detail="No autorizado")


AuthDep = Annotated[UserResponse, Depends(get_current_user_dep)]


def require_permission(permission: str):
    def _check(
        db: SupabaseDep,
        token: TokenDep,
    ) -> UserResponse:
        try:
            user = get_current_user(db, token)
        except Exception:
            raise HTTPException(status_code=401, detail="No autorizado")
        if permission not in user.permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Permiso requerido: {permission}",
            )
        return user
    return _check
