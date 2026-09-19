from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.dependencies import SupabaseDep, require_permission
from app.schemas.auth import UserResponse
from app.services.crud import TableRepository
from app.services.excel_generator import (
    generate_candidatos_excel,
    generate_no_proceden_excel,
    generate_propuestas_excel,
    generate_reajustes_excel,
)

router = APIRouter(prefix="/exportar-excel", tags=["Exportación"])

EXCEL_TYPES = {
    "candidatos": ("candidatos", generate_candidatos_excel),
    "propuestas": ("propuestas", generate_propuestas_excel),
    "reajustes": ("reajustes", generate_reajustes_excel),
    "no_proceden": ("no_proceden", generate_no_proceden_excel),
}


@router.get("/{tabla}")
def exportar_excel(
    tabla: str,
    db: SupabaseDep,
    user: UserResponse = Depends(require_permission("exportar")),
):
    if tabla not in EXCEL_TYPES:
        raise HTTPException(
            status_code=404,
            detail=f"Tabla '{tabla}' no encontrada. "
                   f"Opciones: {list(EXCEL_TYPES.keys())}",
        )

    table_name, excel_func = EXCEL_TYPES[tabla]
    data = TableRepository(db, table_name).list_all()

    output = excel_func(data)
    filename = f"{tabla}_export.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )