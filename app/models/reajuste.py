import uuid
from datetime import date, datetime

from sqlmodel import Field as SQLModelField
from sqlmodel import SQLModel


class Reajuste(SQLModel, table=True):
    __tablename__ = "reajustes"

    id: uuid.UUID = SQLModelField(
        default_factory=uuid.uuid4, primary_key=True
    )
    cedula: str = SQLModelField(max_length=20)
    nombre_completo: str = SQLModelField(max_length=255)
    grupo_ocupacional: str | None = SQLModelField(default=None, max_length=255)
    cargo: str | None = SQLModelField(default=None, max_length=255)
    salario_actual: float = SQLModelField(default=0.0)
    salario_solicitado: float = SQLModelField(default=0.0)
    observacion: str | None = SQLModelField(default=None, max_length=1000)
    diferencia_salarial: float = SQLModelField(default=0.0)
    porcentaje_incremento: float = SQLModelField(default=0.0)
    fecha_efectividad: date | None = SQLModelField(default=None)
    created_at: datetime = SQLModelField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLModelField(default_factory=datetime.utcnow)
