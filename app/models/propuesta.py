import uuid
from datetime import date, datetime

from sqlmodel import Field as SQLModelField
from sqlmodel import SQLModel


class Propuesta(SQLModel, table=True):
    __tablename__ = "propuestas"

    id: uuid.UUID = SQLModelField(
        default_factory=uuid.uuid4, primary_key=True
    )
    no: int = SQLModelField(index=True)
    reg_dist: str | None = SQLModelField(default=None, max_length=100)
    cedula: str = SQLModelField(max_length=20)
    nombre_completo: str = SQLModelField(max_length=255)
    sexo: str | None = SQLModelField(default=None, max_length=20)
    cargo_solicitado: str | None = SQLModelField(default=None, max_length=255)
    cargo_aprobado: str | None = SQLModelField(default=None, max_length=255)
    escolaridad: str | None = SQLModelField(default=None, max_length=255)
    en_sustitucion_de: str | None = SQLModelField(default=None, max_length=255)
    cedula_no: str | None = SQLModelField(default=None, max_length=20)
    fecha_ingreso: date | None = SQLModelField(default=None)
    centro: str | None = SQLModelField(default=None, max_length=255)
    referido_por: str | None = SQLModelField(default=None, max_length=255)
    telefono: str | None = SQLModelField(default=None, max_length=50)
    created_at: datetime = SQLModelField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLModelField(default_factory=datetime.utcnow)
