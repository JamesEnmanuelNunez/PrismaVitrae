from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import AuthDep, SupabaseDep, require_permission
from app.schemas.auth import UserResponse
from app.schemas.candidato import CandidatoCreate, CandidatoRead, CandidatoUpdate
from app.services.supabase_storage import delete_file

router = APIRouter(prefix="/candidatos", tags=["Candidatos"])

TABLE = "candidatos"


@router.get("/", response_model=list[CandidatoRead])
def list_candidatos(
    db: SupabaseDep,
    user: AuthDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    result = db.table(TABLE).select("*").range(offset, offset + limit - 1).execute()
    return result.data


@router.post("/", response_model=CandidatoRead, status_code=201)
def create_candidato(data: CandidatoCreate, db: SupabaseDep, user: UserResponse = Depends(require_permission("crear"))):
    result = db.table(TABLE).insert(data.model_dump()).execute()
    return result.data[0]


@router.get("/{candidato_id}", response_model=CandidatoRead)
def get_candidato(candidato_id: str, db: SupabaseDep, user: AuthDep):
    result = db.table(TABLE).select("*").eq("id", candidato_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Candidato no encontrado")
    return result.data[0]


@router.put("/{candidato_id}", response_model=CandidatoRead)
def update_candidato(candidato_id: str, data: CandidatoUpdate, db: SupabaseDep, user: UserResponse = Depends(require_permission("editar"))):
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Sin datos para actualizar")

    result = (
        db.table(TABLE)
        .update(update_data)
        .eq("id", candidato_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Candidato no encontrado")
    return result.data[0]


@router.delete("/{candidato_id}", status_code=204)
def delete_candidato(candidato_id: str, db: SupabaseDep, user: UserResponse = Depends(require_permission("eliminar"))):
    existing = db.table(TABLE).select("archivo_url").eq("id", candidato_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Candidato no encontrado")

    if existing.data[0].get("archivo_url"):
        delete_file(existing.data[0]["archivo_url"])

    db.table(TABLE).delete().eq("id", candidato_id).execute()
