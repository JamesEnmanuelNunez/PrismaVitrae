import os
import tempfile
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.dependencies import SupabaseDep, require_permission
from app.schemas.auth import UserResponse
from app.schemas.candidato import CandidatoRead
from app.services.ai_extractor import extract_document_data
from app.services.supabase_storage import upload_file

router = APIRouter(prefix="/escanear", tags=["Scanner"])

ALLOWED_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

TABLE = "candidatos"


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


def extract_first_name(full_name: str) -> str:
    parts = normalize_text(full_name).split()
    return parts[0] if parts else ""


def extract_first_last_name(full_name: str) -> str:
    parts = normalize_text(full_name).split()
    return parts[-1] if len(parts) > 1 else ""


def find_matching_candidato(
    db: SupabaseDep, primer_nombre: str, primer_apellido: str
) -> dict | None:
    if not primer_nombre or not primer_apellido:
        return None
        
    result = db.table(TABLE).select("*").execute()
    for c in result.data:
        crudos = c.get("datos_crudos") or {}
        # Primero intentamos sacar los nombres de la extracción previa si existen
        existing_nombre = crudos.get("primer_nombre", "")
        existing_apellido = crudos.get("primer_apellido", "")
        
        # Si no existían en datos_crudos, intentamos inferirlos del nombre completo
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
                
        if existing_nombre == primer_nombre and existing_apellido == primer_apellido:
            return c
    return None


@router.post("/", response_model=CandidatoRead)
async def escanear_documento(
    db: SupabaseDep,
    file: UploadFile,
    user: UserResponse = Depends(require_permission("escanear")),
):
    if file.content_type not in ALLOWED_TYPES:
        ext = file.filename.split(".")[-1] if file.filename else "unknown"
        if f".{ext}" not in ALLOWED_TYPES.values():
            raise HTTPException(
                status_code=422,
                detail=f"Tipo de archivo no permitido: {file.content_type}. "
                       "Use PDF, JPG, PNG o WEBP.",
            )

    suffix = ALLOWED_TYPES.get(file.content_type, ".pdf")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        extracted_data = await extract_document_data(tmp_path)
        tipo_documento = extracted_data.get("tipo_documento", "CV")
        datos = extracted_data.get("datos", {})
        primer_nombre = extracted_data.get("primer_nombre", "")
        primer_apellido = extracted_data.get("primer_apellido", "")

        if tipo_documento == "CEDULA":
            file_url = upload_file(tmp_path, folder="cedulas")
            existing = find_matching_candidato(
                db, primer_nombre, primer_apellido
            )
            if existing:
                update_data = {
                    "cedula": datos.get("cedula"),
                    "sexo": datos.get("sexo"),
                    "cedula_url": file_url,
                    "datos_crudos": {
                        **(existing.get("datos_crudos") or {}),
                        "cedula_datos": extracted_data,
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
                    "cedula": datos.get("cedula"),
                    "sexo": datos.get("sexo"),
                    "cedula_url": file_url,
                    "datos_crudos": extracted_data,
                }
                result = db.table(TABLE).insert(candidato_data).execute()
                return result.data[0]

        else:
            file_url = upload_file(tmp_path, folder="cvs")
            existing = find_matching_candidato(
                db, primer_nombre, primer_apellido
            )
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
                    "confianza": extracted_data.get("tipo_confianza"),
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
                    "confianza": extracted_data.get("tipo_confianza"),
                }
                result = db.table(TABLE).insert(candidato_data).execute()
                return result.data[0]
    finally:
        os.unlink(tmp_path)
