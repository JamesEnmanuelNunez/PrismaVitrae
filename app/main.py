import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.exceptions import PrismaVitaeError
from app.routers import (
    auth_router,
    candidates_router,
    export_router,
    no_proceden_router,
    propuestas_router,
    reajustes_router,
    scanner_router,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("prismavitae")

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend para gestión de CVs y tablas R.J.C.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(PrismaVitaeError)
async def handle_domain_error(request: Request, exc: PrismaVitaeError) -> JSONResponse:
    logger.error("Error %s en %s: %s", exc.status_code, request.url.path, exc)
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Error no controlado en %s", request.url.path)
    return JSONResponse(
        status_code=500, content={"detail": "Error interno del servidor"}
    )


for router in [
    auth_router,
    scanner_router,
    export_router,
    candidates_router,
    propuestas_router,
    reajustes_router,
    no_proceden_router,
]:
    app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "PrismaVitae API is running",
        "env": settings.APP_ENV,
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}