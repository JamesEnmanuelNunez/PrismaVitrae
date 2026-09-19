from app.schemas.reajuste import ReajusteCreate, ReajusteRead, ReajusteUpdate
from app.services.crud import build_crud_router

router = build_crud_router(
    table="reajustes",
    prefix="/reajustes",
    tag="Reajustes",
    resource_name="Reajuste",
    read_permission="ver_reajustes",
    create_schema=ReajusteCreate,
    read_schema=ReajusteRead,
    update_schema=ReajusteUpdate,
)