import os
import tempfile
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.config import settings
from app.constants import ALLOWED_MIME_TYPES, MIME_TO_EXTENSION
from app.dependencies import SupabaseDep, require_permission
from app.exceptions import ValidationError
from app.schemas.auth import UserResponse
from app.schemas.candidato import CandidatoRead
from app.services.ai_extractor import extract_document_data
from app.services.crud import TableRepository
from app.services.supabase_storage import upload_file

router = APIRouter(prefix="/escanear", tags=["Scanner"])

TABLE = "candidatos"
MATCH_PAGE_SIZE = 1000
MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_MB * 1024 * 1024


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


def _matches_candidato(c: dict, primer_nombre: str, primer_apellido: str) -> bool:
    crudos = c.get("datos_crudos") or {}
    existing_nombre = crudos.get("primer_nombre", "")
    existing_apellido = crudos.get("primer_apellido", "")

    if not existing_nombre or not existing_apellido:
        parts = normalize_text(c.get("nombre", "")).split()
        existing_nombre = parts[0] if parts else ""
        if len(parts) == 2:
            existing_apellido = parts[1]
        elif len(parts) == 3:
            existing_apellido = parts[1]
        elif len(parts) >= 4:
            existing_apellido = parts[2]
        else:
            existing_apellido = ""

    return existing_nombre == primer_nombre and existing_apellido == primer_apellido


def find_matching_candidato(
    db: SupabaseDep, primer_nombre: str, primer_apellido: str
) -> dict | None:
    """Busca un candidato por nombre/apellido normalizados, paginando para no
    depender del límite por defecto de PostgREST (~1000 filas)."""
    if not primer_nombre or not primer_apellido:
        return None

    repo = TableRepository(db, TABLE)
    for c in repo.list_all(page_size=MATCH_PAGE_SIZE):
        if _matches_candidato(c, primer_nombre, primer_apellido):
            return c
    return None


def parse_confianza(val) -> float:
    try:
        if val is None:
            return 0.0
        if isinstance(val, str):
            val = val.replace("%", "").strip()
        f = float(val)
        if f > 1.0:
            f = f / 100.0
        return f
    except Exception:
        return 0.0


@router.post("/", response_model=CandidatoRead)
async def escanear_documento(
    db: SupabaseDep,
    file: UploadFile,
    user: UserResponse = Depends(require_permission("escanear")),
):
    content_type = file.content_type.lower() if file.content_type else ""
    if content_type == "image/jpg":
        content_type = "image/jpeg"

    if content_type not in MIME_TO_EXTENSION:
        ext = file.filename.lower().split(".")[-1] if file.filename else "unknown"
        valid_ext = f".{ext}"
        if valid_ext not in ALLOWED_MIME_TYPES:
            raise ValidationError(
                f"Tipo de archivo no permitido: {file.content_type}. "
                "Use PDF, JPG, PNG, WEBP o HEIC.",
            )
        suffix = valid_ext
    else:
        suffix = MIME_TO_EXTENSION.get(content_type, ".pdf")

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Archivo demasiado grande. Máximo {settings.MAX_UPLOAD_MB} MB.",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        extracted_data = await extract_document_data(tmp_path)
        tipo_documento = extracted_data.get("tipo_documento", "CV")
        datos = extracted_data.get("datos", {})
        primer_nombre = extracted_data.get("primer_nombre", "")
        primer_apellido = extracted_data.get("primer_apellido", "")
        confianza_val = parse_confianza(extracted_data.get("tipo_confianza"))

        if tipo_documento == "CEDULA":
            file_url = upload_file(db, tmp_path, folder="cedulas")
            existing = find_matching_candidato(db, primer_nombre, primer_apellido)
            if existing:
                update_data = {
                    "datos_crudos": {
                        **(existing.get("datos_crudos") or {}),
                        "cedula_datos": extracted_data,
                        "cedula": datos.get("cedula"),
                        "sexo": datos.get("sexo"),
                        "cedula_url": file_url,
                    },
                }
                result = (
                    db.table(TABLE)
                    .update(update_data)
                    .eq("id", existing["id"])
                    .execute()
                )
                return result.data[0]
            else:
                candidato_data = {
                    "nombre": datos.get("nombre", "Sin nombre"),
                    "datos_crudos": {
                        **extracted_data,
                        "cedula_url": file_url,
                    },
                }
                result = db.table(TABLE).insert(candidato_data).execute()
                return result.data[0]

        else:
            file_url = upload_file(db, tmp_path, folder="cvs")
            existing = find_matching_candidato(db, primer_nombre, primer_apellido)
            if existing:
                update_data = {
                    "nombre": datos.get("nombre", existing.get("nombre")),
                    "telefono": datos.get("telefono"),
                    "email": datos.get("email"),
                    "habilidades": datos.get("habilidades", []),
                    "experiencia_anios": datos.get("experiencia_anios"),
                    "educacion": datos.get("educacion"),
                    "resumen": datos.get("resumen"),
                    "archivo_url": file_url,
                    "confianza": confianza_val,
                    "datos_crudos": {
                        **(existing.get("datos_crudos") or {}),
                        "cv_datos": extracted_data,
                    },
                }
                result = (
                    db.table(TABLE)
                    .update(update_data)
                    .eq("id", existing["id"])
                    .execute()
                )
                return result.data[0]
            else:
                candidato_data = {
                    "nombre": datos.get("nombre", "Sin nombre"),
                    "telefono": datos.get("telefono"),
                    "email": datos.get("email"),
                    "habilidades": datos.get("habilidades", []),
                    "experiencia_anios": datos.get("experiencia_anios"),
                    "educacion": datos.get("educacion"),
                    "resumen": datos.get("resumen"),
                    "archivo_url": file_url,
                    "datos_crudos": extracted_data,
                    "confianza": confianza_val,
                }
                result = db.table(TABLE).insert(candidato_data).execute()
                return result.data[0]
    finally:
        os.unlink(tmp_path)