from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    auth_router,
    candidates_router,
    export_router,
    no_proceden_router,
    propuestas_router,
    reajustes_router,
    scanner_router,
)

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend para gestión de CVs y tablas R.J.C.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173",
        "https://prismavitae.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(scanner_router, prefix="/api")
app.include_router(export_router, prefix="/api")
app.include_router(candidates_router, prefix="/api")
app.include_router(propuestas_router, prefix="/api")
app.include_router(reajustes_router, prefix="/api")
app.include_router(no_proceden_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "PrismaVitae API is running", "env": settings.APP_ENV}


@app.get("/health")
async def health():
    return {"status": "healthy"}
