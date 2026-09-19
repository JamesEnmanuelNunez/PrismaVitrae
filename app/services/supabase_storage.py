import uuid
from pathlib import Path

from supabase import Client

from app.config import settings
from app.constants import ALLOWED_MIME_TYPES
from app.exceptions import StorageError

BUCKET_NAME = settings.STORAGE_BUCKET


def upload_file(db: Client, file_path: str, folder: str = "uploads") -> str:
    path = Path(file_path)
    ext = path.suffix.lower()
    filename = f"{folder}/{uuid.uuid4()}{ext}"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    content_type = ALLOWED_MIME_TYPES.get(ext, "application/octet-stream")

    try:
        db.storage.from_(BUCKET_NAME).upload(
            path=filename,
            file=file_bytes,
            file_options={"content-type": content_type},
        )
    except Exception as exc:
        raise StorageError(f"Error al subir el archivo: {exc}") from exc

    public_url = db.storage.from_(BUCKET_NAME).get_public_url(filename)
    return public_url


def delete_file(db: Client, file_url: str) -> bool:
    parts = file_url.split(f"/{BUCKET_NAME}/")
    if len(parts) < 2:
        return False
    file_path = parts[1]
    db.storage.from_(BUCKET_NAME).remove([file_path])
    return True