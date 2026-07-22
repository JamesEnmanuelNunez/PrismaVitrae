import uuid
from pathlib import Path

from supabase import create_client

from app.config import settings

BUCKET_NAME = "cvs"

client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def upload_file(file_path: str, folder: str = "uploads") -> str:
    path = Path(file_path)
    ext = path.suffix
    filename = f"{folder}/{uuid.uuid4()}{ext}"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    mime_types = {
        ".pdf": "application/pdf",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
    }
    content_type = mime_types.get(ext, "application/octet-stream")

    client.storage.from_(BUCKET_NAME).upload(
        path=filename,
        file=file_bytes,
        file_options={"content-type": content_type},
    )

    public_url = client.storage.from_(BUCKET_NAME).get_public_url(filename)
    return public_url


def delete_file(file_url: str) -> bool:
    try:
        parts = file_url.split(f"/{BUCKET_NAME}/")
        if len(parts) < 2:
            return False
        file_path = parts[1]
        client.storage.from_(BUCKET_NAME).remove([file_path])
        return True
    except Exception:
        return False
