import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class PropuestaBase(BaseModel):
    no: int
    reg_dist: str | None = Field(default=None, max_length=100)
    cedula: str = Field(max_length=20)
    nombre_completo: str = Field(max_length=255)
    sexo: str | None = Field(default=None, max_length=20)
    cargo_solicitado: str | None = Field(default=None, max_length=255)
    cargo_aprobado: str | None = Field(default=None, max_length=255)
    escolaridad: str | None = Field(default=None, max_length=255)
    en_sustitucion_de: str | None = Field(default=None, max_length=255)
    cedula_no: str | None = Field(default=None, max_length=20)
    fecha_ingreso: date | None = None
    centro: str | None = Field(default=None, max_length=255)
    referido_por: str | None = Field(default=None, max_length=255)
    telefono: str | None = Field(default=None, max_length=50)


class PropuestaCreate(PropuestaBase):
    pass


class PropuestaUpdate(BaseModel):
    no: int | None = None
    reg_dist: str | None = Field(default=None, max_length=100)
    cedula: str | None = Field(default=None, max_length=20)
    nombre_completo: str | None = Field(default=None, max_length=255)
    sexo: str | None = Field(default=None, max_length=20)
    cargo_solicitado: str | None = Field(default=None, max_length=255)
    cargo_aprobado: str | None = Field(default=None, max_length=255)
    escolaridad: str | None = Field(default=None, max_length=255)
    en_sustitucion_de: str | None = Field(default=None, max_length=255)
    cedula_no: str | None = Field(default=None, max_length=20)
    fecha_ingreso: date | None = None
    centro: str | None = Field(default=None, max_length=255)
    referido_por: str | None = Field(default=None, max_length=255)
    telefono: str | None = Field(default=None, max_length=50)


class PropuestaRead(PropuestaBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
