from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import AuthDep, SupabaseDep, require_permission
from app.schemas.auth import UserResponse
from app.schemas.reajuste import ReajusteCreate, ReajusteRead, ReajusteUpdate

router = APIRouter(prefix="/reajustes", tags=["Reajustes"])

TABLE = "reajustes"


@router.get("/", response_model=list[ReajusteRead])
def list_reajustes(
    db: SupabaseDep,
    user: AuthDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    result = db.table(TABLE).select("*").range(offset, offset + limit - 1).execute()
    return result.data


@router.post("/", response_model=ReajusteRead, status_code=201)
def create_reajuste(data: ReajusteCreate, db: SupabaseDep, user: UserResponse = Depends(require_permission("crear"))):
    result = db.table(TABLE).insert(data.model_dump()).execute()
    return result.data[0]


@router.get("/{reajuste_id}", response_model=ReajusteRead)
def get_reajuste(reajuste_id: str, db: SupabaseDep, user: AuthDep):
    result = db.table(TABLE).select("*").eq("id", reajuste_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Reajuste no encontrado")
    return result.data[0]


@router.put("/{reajuste_id}", response_model=ReajusteRead)
def update_reajuste(reajuste_id: str, data: ReajusteUpdate, db: SupabaseDep, user: UserResponse = Depends(require_permission("editar"))):
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Sin datos para actualizar")

    result = (
        db.table(TABLE).update(update_data).eq("id", reajuste_id).execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Reajuste no encontrado")
    return result.data[0]


@router.delete("/{reajuste_id}", status_code=204)
def delete_reajuste(reajuste_id: str, db: SupabaseDep, user: UserResponse = Depends(require_permission("eliminar"))):
    existing = db.table(TABLE).select("id").eq("id", reajuste_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Reajuste no encontrado")

    db.table(TABLE).delete().eq("id", reajuste_id).execute()
