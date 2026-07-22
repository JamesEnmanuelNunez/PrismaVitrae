from app.routers.auth import router as auth_router
from app.routers.candidates import router as candidates_router
from app.routers.export import router as export_router
from app.routers.no_proceden import router as no_proceden_router
from app.routers.propuestas import router as propuestas_router
from app.routers.reajustes import router as reajustes_router
from app.routers.scanner import router as scanner_router

__all__ = [
    "auth_router",
    "candidates_router",
    "export_router",
    "no_proceden_router",
    "propuestas_router",
    "reajustes_router",
    "scanner_router",
]
