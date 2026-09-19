"""Promueve un usuario a administrador (rol admin + todos los permisos).

Uso:
    uv run python -m scripts.create_admin usuario@example.com

Requiere SUPABASE_URL y SUPABASE_SERVICE_KEY en .env. Pensado para crear el
primer admin tras restaurar el flujo de aprobación de cuentas.
"""

import sys

from supabase import create_client

from app.config import settings
from app.services.auth import DEFAULT_PERMISSIONS


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: uv run python -m scripts.create_admin <email>")
        sys.exit(1)

    email = sys.argv[1].strip().lower()

    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        print("Faltan SUPABASE_URL y/o SUPABASE_SERVICE_KEY en .env")
        sys.exit(1)

    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    result = (
        client.table("user_profiles")
        .update({
            "role": "admin",
            "status": "approved",
            "permissions": DEFAULT_PERMISSIONS["admin"],
        })
        .eq("email", email)
        .execute()
    )

    if not result.data:
        print(f"No se encontró el perfil para {email}. ¿Se registró primero?")
        sys.exit(1)

    print(f"Usuario {email} promovido a admin.")


if __name__ == "__main__":
    main()
