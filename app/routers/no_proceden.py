from app.schemas.no_procede import NoProcedeCreate, NoProcedeRead, NoProcedeUpdate
from app.services.crud import build_crud_router

router = build_crud_router(
    table="no_proceden",
    prefix="/no-proceden",
    tag="No Proceden",
    resource_name="Registro",
    read_permission="ver_no_proceden",
    create_schema=NoProcedeCreate,
    read_schema=NoProcedeRead,
    update_schema=NoProcedeUpdate,
)