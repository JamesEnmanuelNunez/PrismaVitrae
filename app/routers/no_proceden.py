from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import AuthDep, SupabaseDep, require_permission
from app.schemas.auth import UserResponse
from app.schemas.no_procede import NoProcedeCreate, NoProcedeRead, NoProcedeUpdate

router = APIRouter(prefix="/no-proceden", tags=["No Proceden"])

TABLE = "no_proceden"


@router.get("/", response_model=list[NoProcedeRead])
def list_no_proceden(
    db: SupabaseDep,
    user: AuthDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    result = db.table(TABLE).select("*").range(offset, offset + limit - 1).execute()
    return result.data


@router.post("/", response_model=NoProcedeRead, status_code=201)
def create_no_procede(data: NoProcedeCreate, db: SupabaseDep, user: UserResponse = Depends(require_permission("crear"))):
    result = db.table(TABLE).insert(data.model_dump()).execute()
    return result.data[0]


@router.get("/{no_procede_id}", response_model=NoProcedeRead)
def get_no_procede(no_procede_id: str, db: SupabaseDep, user: AuthDep):
    result = db.table(TABLE).select("*").eq("id", no_procede_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return result.data[0]


@router.put("/{no_procede_id}", response_model=NoProcedeRead)
def update_no_procede(no_procede_id: str, data: NoProcedeUpdate, db: SupabaseDep, user: UserResponse = Depends(require_permission("editar"))):
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Sin datos para actualizar")

    result = (
        db.table(TABLE).update(update_data).eq("id", no_procede_id).execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return result.data[0]


@router.delete("/{no_procede_id}", status_code=204)
def delete_no_procede(no_procede_id: str, db: SupabaseDep, user: UserResponse = Depends(require_permission("eliminar"))):
    existing = db.table(TABLE).select("id").eq("id", no_procede_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    db.table(TABLE).delete().eq("id", no_procede_id).execute()
