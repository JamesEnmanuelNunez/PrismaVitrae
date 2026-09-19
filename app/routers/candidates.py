from supabase import Client

from app.schemas.candidato import CandidatoCreate, CandidatoRead, CandidatoUpdate
from app.services.crud import build_crud_router
from app.services.supabase_storage import delete_file


def _delete_storage_files(db: Client, existing: dict) -> None:
    crudos = existing.get("datos_crudos") or {}
    urls = [existing.get("archivo_url"), crudos.get("cedula_url")]
    for url in urls:
        if url:
            delete_file(db, url)


router = build_crud_router(
    table="candidatos",
    prefix="/candidatos",
    tag="Candidatos",
    resource_name="Candidato",
    read_permission="ver_candidatos",
    create_schema=CandidatoCreate,
    read_schema=CandidatoRead,
    update_schema=CandidatoUpdate,
    before_delete=_delete_storage_files,
)