import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class ReajusteBase(BaseModel):
    cedula: str = Field(max_length=20)
    nombre_completo: str = Field(max_length=255)
    grupo_ocupacional: str | None = Field(default=None, max_length=255)
    cargo: str | None = Field(default=None, max_length=255)
    salario_actual: float = Field(default=0.0, ge=0)
    salario_solicitado: float = Field(default=0.0, ge=0)
    observacion: str | None = Field(default=None, max_length=1000)
    diferencia_salarial: float = Field(default=0.0)
    porcentaje_incremento: float = Field(default=0.0, ge=0, le=100)
    fecha_efectividad: date | None = None


class ReajusteCreate(ReajusteBase):
    pass


class ReajusteUpdate(BaseModel):
    cedula: str | None = Field(default=None, max_length=20)
    nombre_completo: str | None = Field(default=None, max_length=255)
    grupo_ocupacional: str | None = Field(default=None, max_length=255)
    cargo: str | None = Field(default=None, max_length=255)
    salario_actual: float | None = Field(default=None, ge=0)
    salario_solicitado: float | None = Field(default=None, ge=0)
    observacion: str | None = Field(default=None, max_length=1000)
    diferencia_salarial: float | None = None
    porcentaje_incremento: float | None = Field(default=None, ge=0, le=100)
    fecha_efectividad: date | None = None


class ReajusteRead(ReajusteBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
