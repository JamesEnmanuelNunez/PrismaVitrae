"""Lista los usuarios registrados en la tabla `user_profiles`.

Uso:
    uv run python -m scripts.list_users

Requiere SUPABASE_URL y SUPABASE_SERVICE_KEY en .env.
"""

from supabase import create_client

from app.config import settings


def main() -> None:
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    result = client.table("user_profiles").select("email").execute()

    for user in result.data:
        print(user["email"])


if __name__ == "__main__":
    main()
