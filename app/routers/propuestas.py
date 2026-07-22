from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import AuthDep, SupabaseDep, require_permission
from app.schemas.auth import UserResponse
from app.schemas.propuesta import PropuestaCreate, PropuestaRead, PropuestaUpdate

router = APIRouter(prefix="/propuestas", tags=["Propuestas"])

TABLE = "propuestas"


@router.get("/", response_model=list[PropuestaRead])
def list_propuestas(
    db: SupabaseDep,
    user: AuthDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    result = db.table(TABLE).select("*").range(offset, offset + limit - 1).execute()
    return result.data


@router.post("/", response_model=PropuestaRead, status_code=201)
def create_propuesta(data: PropuestaCreate, db: SupabaseDep, user: UserResponse = Depends(require_permission("crear"))):
    result = db.table(TABLE).insert(data.model_dump()).execute()
    return result.data[0]


@router.get("/{propuesta_id}", response_model=PropuestaRead)
def get_propuesta(propuesta_id: str, db: SupabaseDep, user: AuthDep):
    result = db.table(TABLE).select("*").eq("id", propuesta_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    return result.data[0]


@router.put("/{propuesta_id}", response_model=PropuestaRead)
def update_propuesta(propuesta_id: str, data: PropuestaUpdate, db: SupabaseDep, user: UserResponse = Depends(require_permission("editar"))):
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Sin datos para actualizar")

    result = (
        db.table(TABLE).update(update_data).eq("id", propuesta_id).execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    return result.data[0]


@router.delete("/{propuesta_id}", status_code=204)
def delete_propuesta(propuesta_id: str, db: SupabaseDep, user: UserResponse = Depends(require_permission("eliminar"))):
    existing = db.table(TABLE).select("id").eq("id", propuesta_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")

    db.table(TABLE).delete().eq("id", propuesta_id).execute()
