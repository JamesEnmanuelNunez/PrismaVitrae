import asyncio
import logging
from pathlib import Path

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.config import settings
from app.constants import ALLOWED_MIME_TYPES
from app.exceptions import ExtractionError

logger = logging.getLogger(__name__)

_client: genai.Client | None = None


class ExtractionData(BaseModel):
    tipo_documento: str
    tipo_confianza: float
    primer_nombre: str = ""
    primer_apellido: str = ""
    datos: dict


EXTRACTION_PROMPT = (
    "Analiza el documento adjunto y clasifícalo como CV (currículum vitae) "
    "o CEDULA (cédula de identidad).\n"
    "\n"
    "Campos de la respuesta:\n"
    '- "tipo_documento": "CV" o "CEDULA".\n'
    '- "tipo_confianza": confianza de la clasificación entre 0.0 y 1.0.\n'
    '- "primer_nombre": primera palabra del nombre, en minúsculas y sin acentos.\n'
    '- "primer_apellido": primera palabra del apellido, en minúsculas y sin acentos.\n'
    '- "datos": objeto con los datos extraídos según el tipo:\n'
    "  - Si es CV: nombre, telefono, email, habilidades (lista), "
    "experiencia_anios (número), educacion, resumen.\n"
    "  - Si es CEDULA: nombre, cedula, sexo.\n"
    "\n"
    "Reglas:\n"
    "- Un CV contiene información profesional: habilidades, experiencia, "
    "educación, email, teléfono.\n"
    "- Una CÉDULA contiene: número de cédula, nombre completo, fecha de "
    "nacimiento, sexo, nacionalidad.\n"
    "- Normaliza primer_nombre y primer_apellido: minúsculas, sin acentos "
    '(ej. "á" → "a", "ñ" → "n").\n'
    '- Ejemplo: "Juan Antonio Pérez López" → primer_nombre: "juan", '
    'primer_apellido: "perez".'
)


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def _extract_sync(file_path: str, suffix: str) -> dict:
    client = get_client()

    if suffix == ".pdf":
        uploaded_file = client.files.upload(file=str(file_path))
        contents = [EXTRACTION_PROMPT, uploaded_file]
    else:
        mime_type = ALLOWED_MIME_TYPES.get(suffix, "image/jpeg")
        with open(file_path, "rb") as f:
            image_bytes = f.read()
        contents = [
            EXTRACTION_PROMPT,
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        ]

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ExtractionData,
        ),
    )

    parsed = response.parsed
    if parsed is None:
        raise ExtractionError("El modelo no devolvió una respuesta estructurada")
    return parsed.model_dump()


async def extract_document_data(file_path: str) -> dict:
    path = Path(file_path)
    suffix = path.suffix.lower()

    try:
        return await asyncio.to_thread(_extract_sync, file_path, suffix)
    except ExtractionError:
        raise
    except Exception as exc:
        logger.exception("Error al extraer datos del documento %s", file_path)
        raise ExtractionError(f"Error al extraer datos del documento: {exc}") from exc