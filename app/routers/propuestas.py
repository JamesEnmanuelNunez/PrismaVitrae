from app.schemas.propuesta import PropuestaCreate, PropuestaRead, PropuestaUpdate
from app.services.crud import build_crud_router

router = build_crud_router(
    table="propuestas",
    prefix="/propuestas",
    tag="Propuestas",
    resource_name="Propuesta",
    read_permission="ver_propuestas",
    create_schema=PropuestaCreate,
    read_schema=PropuestaRead,
    update_schema=PropuestaUpdate,
)