from collections.abc import Callable

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from supabase import Client

from app.dependencies import SupabaseDep, require_permission
from app.exceptions import NotFoundError, PrismaVitaeError
from app.schemas.auth import UserResponse


class TableRepository:
    """Acceso genérico a una tabla de Supabase (PostgREST)."""

    def __init__(self, db: Client, table: str, resource_name: str = "Registro"):
        self._db = db
        self._table = table
        self._resource = resource_name

    def list(self, offset: int, limit: int) -> list[dict]:
        result = (
            self._db.table(self._table)
            .select("*")
            .range(offset, offset + limit - 1)
            .execute()
        )
        return result.data

    def list_all(self, page_size: int = 1000) -> list[dict]:
        """Itera la paginación de PostgREST y devuelve todas las filas."""
        rows: list[dict] = []
        offset = 0
        while True:
            page = self.list(offset, page_size)
            if not page:
                break
            rows.extend(page)
            if len(page) < page_size:
                break
            offset += page_size
        return rows

    def create(self, data: dict) -> dict:
        result = self._db.table(self._table).insert(data).execute()
        return result.data[0]

    def get(self, item_id: str) -> dict:
        result = self._db.table(self._table).select("*").eq("id", item_id).execute()
        if not result.data:
            raise NotFoundError(f"{self._resource} no encontrado")
        return result.data[0]

    def update(self, item_id: str, data: dict) -> dict:
        if not data:
            raise PrismaVitaeError("Sin datos para actualizar")
        result = (
            self._db.table(self._table).update(data).eq("id", item_id).execute()
        )
        if not result.data:
            raise NotFoundError(f"{self._resource} no encontrado")
        return result.data[0]

    def delete(self, item_id: str) -> None:
        existing = self._db.table(self._table).select("*").eq("id", item_id).execute()
        if not existing.data:
            raise NotFoundError(f"{self._resource} no encontrado")
        self._db.table(self._table).delete().eq("id", item_id).execute()


def build_crud_router(
    *,
    table: str,
    prefix: str,
    tag: str,
    resource_name: str,
    read_permission: str,
    create_schema: type[BaseModel],
    read_schema: type[BaseModel],
    update_schema: type[BaseModel],
    before_delete: Callable[[Client, dict], None] | None = None,
) -> APIRouter:
    """Genera un router CRUD estándar para una tabla de Supabase."""

    router = APIRouter(prefix=prefix, tags=[tag])

    @router.get("/", response_model=list[read_schema])
    def list_items(
        db: SupabaseDep,
        user: UserResponse = Depends(require_permission(read_permission)),
        offset: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
    ):
        return TableRepository(db, table, resource_name).list(offset, limit)

    @router.post("/", response_model=read_schema, status_code=201)
    def create_item(
        data: create_schema,
        db: SupabaseDep,
        user: UserResponse = Depends(require_permission("crear")),
    ):
        return TableRepository(db, table, resource_name).create(data.model_dump())

    @router.get("/{item_id}", response_model=read_schema)
    def get_item(
        item_id: str,
        db: SupabaseDep,
        user: UserResponse = Depends(require_permission(read_permission)),
    ):
        return TableRepository(db, table, resource_name).get(item_id)

    @router.put("/{item_id}", response_model=read_schema)
    def update_item(
        item_id: str,
        data: update_schema,
        db: SupabaseDep,
        user: UserResponse = Depends(require_permission("editar")),
    ):
        return TableRepository(db, table, resource_name).update(
            item_id, data.model_dump(exclude_unset=True)
        )

    @router.delete("/{item_id}", status_code=204)
    def delete_item(
        item_id: str,
        db: SupabaseDep,
        user: UserResponse = Depends(require_permission("eliminar")),
    ):
        repo = TableRepository(db, table, resource_name)
        existing = repo.get(item_id)
        if before_delete:
            before_delete(db, existing)
        repo.delete(item_id)

    return router