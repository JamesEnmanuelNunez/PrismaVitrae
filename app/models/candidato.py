import uuid
from datetime import datetime

from sqlalchemy import JSON, Column
from sqlmodel import Field as SQLModelField
from sqlmodel import SQLModel


class Candidato(SQLModel, table=True):
    __tablename__ = "candidatos"

    id: uuid.UUID = SQLModelField(
        default_factory=uuid.uuid4, primary_key=True
    )
    nombre: str = SQLModelField(max_length=255)
    telefono: str | None = SQLModelField(default=None, max_length=50)
    email: str | None = SQLModelField(default=None, max_length=255)
    habilidades: list[str] = SQLModelField(
        default_factory=list, sa_column=Column(JSON)
    )
    experiencia_anios: float | None = SQLModelField(default=None)
    educacion: str | None = SQLModelField(default=None, max_length=500)
    resumen: str | None = SQLModelField(default=None, max_length=2000)
    archivo_url: str | None = SQLModelField(default=None, max_length=500)
    datos_crudos: dict | None = SQLModelField(
        default=None, sa_column=Column(JSON)
    )
    confianza: float | None = SQLModelField(default=None)
    created_at: datetime = SQLModelField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLModelField(default_factory=datetime.utcnow)
