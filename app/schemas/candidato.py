import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CandidatoBase(BaseModel):
    nombre: str = Field(max_length=255)
    telefono: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=255)
    habilidades: list[str] = Field(default_factory=list)
    experiencia_anios: float | None = None
    educacion: str | None = Field(default=None, max_length=500)
    resumen: str | None = Field(default=None, max_length=2000)
    archivo_url: str | None = Field(default=None, max_length=500)
    datos_crudos: dict | None = None
    confianza: float | None = None


class CandidatoCreate(CandidatoBase):
    pass


class CandidatoUpdate(BaseModel):
    nombre: str | None = Field(default=None, max_length=255)
    telefono: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=255)
    habilidades: list[str] | None = None
    experiencia_anios: float | None = None
    educacion: str | None = Field(default=None, max_length=500)
    resumen: str | None = Field(default=None, max_length=2000)
    archivo_url: str | None = Field(default=None, max_length=500)
    datos_crudos: dict | None = None
    confianza: float | None = None


class CandidatoRead(CandidatoBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}