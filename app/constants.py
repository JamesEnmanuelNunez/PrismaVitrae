"""Constantes compartidas por el backend."""

ALLOWED_MIME_TYPES = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".heic": "image/heic",
}

MIME_TO_EXTENSION = {mime: ext for ext, mime in ALLOWED_MIME_TYPES.items()}
