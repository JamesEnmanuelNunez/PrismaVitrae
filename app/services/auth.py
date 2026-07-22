from supabase import Client

from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)

TABLE = "user_profiles"

DEFAULT_PERMISSIONS = {
    "admin": [
        "escanear", "exportar", "crear", "editar", "eliminar",
        "ver_propuestas", "ver_reajustes", "ver_no_proceden", "ver_candidatos",
        "manage_users",
    ],
    "user": [
        "escanear", "exportar", "crear", "editar",
        "ver_propuestas", "ver_reajustes", "ver_no_proceden", "ver_candidatos",
    ],
    "viewer": [
        "ver_propuestas", "ver_reajustes", "ver_no_proceden", "ver_candidatos",
    ],
}


def register(db: Client, data: RegisterRequest) -> AuthResponse:
    result = db.auth.sign_up({"email": data.email, "password": data.password})
    if result.user is None:
        raise ValueError("Error al registrar usuario")

    user_id = result.user.id
    db.table(TABLE).insert({
        "id": user_id,
        "email": data.email,
        "role": "pending",
        "status": "pending",
        "permissions": [],
        "full_name": data.full_name,
    }).execute()

    return AuthResponse(
        access_token=result.session.access_token,
        user=UserResponse(
            id=user_id,
            email=data.email,
            role="pending",
            status="pending",
            permissions=[],
            full_name=data.full_name,
        ),
    )


def login(db: Client, data: LoginRequest) -> AuthResponse:
    result = db.auth.sign_in_with_password({"email": data.email, "password": data.password})
    if result.user is None:
        raise ValueError("Credenciales inválidas")

    user_id = result.user.id
    profile = db.table(TABLE).select("*").eq("id", user_id).single().execute()

    if profile.data["status"] != "approved":
        raise ValueError("Tu cuenta está pendiente de aprobación por un administrador")

    return AuthResponse(
        access_token=result.session.access_token,
        user=UserResponse(
            id=user_id,
            email=data.email,
            role=profile.data["role"],
            status=profile.data["status"],
            permissions=profile.data["permissions"],
            full_name=profile.data.get("full_name"),
        ),
    )


def get_current_user(db: Client, token: str) -> UserResponse:
    result = db.auth.get_user(token)
    if result.user is None:
        raise ValueError("Token inválido")

    user_id = result.user.id
    profile = db.table(TABLE).select("*").eq("id", user_id).single().execute()

    return UserResponse(
        id=user_id,
        email=result.user.email,
        role=profile.data["role"],
        status=profile.data["status"],
        permissions=profile.data["permissions"],
        full_name=profile.data.get("full_name"),
    )


def approve_user(db: Client, user_id: str, role: str, permissions: list[str] | None = None) -> dict:
    if role not in DEFAULT_PERMISSIONS:
        raise ValueError(f"Rol inválido: {role}")

    final_permissions = permissions if permissions else DEFAULT_PERMISSIONS[role]
    db.table(TABLE).update({
        "role": role,
        "status": "approved",
        "permissions": final_permissions,
    }).eq("id", user_id).execute()
    return {"user_id": user_id, "role": role, "status": "approved", "permissions": final_permissions}


def reject_user(db: Client, user_id: str) -> dict:
    db.table(TABLE).update({
        "status": "rejected",
    }).eq("id", user_id).execute()
    return {"user_id": user_id, "status": "rejected"}


def list_pending_users(db: Client) -> list[dict]:
    result = db.table(TABLE).select("*").eq("status", "pending").execute()
    return result.data


def update_role(db: Client, user_id: str, role: str) -> dict:
    if role not in DEFAULT_PERMISSIONS:
        raise ValueError(f"Rol inválido: {role}")

    permissions = DEFAULT_PERMISSIONS[role]
    db.table(TABLE).update({"role": role, "permissions": permissions}).eq("id", user_id).execute()
    return {"user_id": user_id, "role": role, "permissions": permissions}


def update_permissions(db: Client, user_id: str, permissions: list[str]) -> dict:
    db.table(TABLE).update({"permissions": permissions}).eq("id", user_id).execute()
    return {"user_id": user_id, "permissions": permissions}
