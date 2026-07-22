import uuid
from datetime import datetime

from sqlmodel import Field as SQLModelField
from sqlmodel import SQLModel


class NoProcede(SQLModel, table=True):
    __tablename__ = "no_proceden"

    id: uuid.UUID = SQLModelField(
        default_factory=uuid.uuid4, primary_key=True
    )
    no: int = SQLModelField(index=True)
    reg_dist: str | None = SQLModelField(default=None, max_length=100)
    cedula: str = SQLModelField(max_length=20)
    nombre_completo: str = SQLModelField(max_length=255)
    sexo: str | None = SQLModelField(default=None, max_length=20)
    cargo_solicitado: str | None = SQLModelField(default=None, max_length=255)
    salario_solicitado: float = SQLModelField(default=0.0)
    escolaridad: str | None = SQLModelField(default=None, max_length=255)
    observacion: str | None = SQLModelField(default=None, max_length=1000)
    referido_por: str | None = SQLModelField(default=None, max_length=255)
    telefono: str | None = SQLModelField(default=None, max_length=50)
    created_at: datetime = SQLModelField(default_factory=datetime.utcnow)
    updated_at: datetime = SQLModelField(default_factory=datetime.utcnow)
