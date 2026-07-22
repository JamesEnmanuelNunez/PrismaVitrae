import os
import tempfile

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.dependencies import SupabaseDep, require_permission
from app.schemas.auth import UserResponse
from app.schemas.candidato import CandidatoRead
from app.services.ai_extractor import extract_cv_data
from app.services.supabase_storage import upload_file

router = APIRouter(prefix="/escanear", tags=["Scanner"])

ALLOWED_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

TABLE = "candidatos"


@router.post("/", response_model=CandidatoRead)
async def escanear_cv(
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
        file_url = upload_file(tmp_path, folder="cvs")
        extracted_data = await extract_cv_data(tmp_path)

        candidato_data = {
            "nombre": extracted_data.get("nombre", "Sin nombre"),
            "telefono": extracted_data.get("telefono"),
            "email": extracted_data.get("email"),
            "habilidades": extracted_data.get("habilidades", []),
            "experiencia_anios": extracted_data.get("experiencia_anios"),
            "educacion": extracted_data.get("educacion"),
            "resumen": extracted_data.get("resumen"),
            "archivo_url": file_url,
            "datos_crudos": extracted_data,
            "confianza": extracted_data.get("confianza"),
        }

        result = db.table(TABLE).insert(candidato_data).execute()
        return result.data[0]
    finally:
        os.unlink(tmp_path)
