import json
from pathlib import Path

from google import genai
from google.genai import types

from app.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

EXTRACTION_PROMPT = """Extrae la siguiente información del currículum vitae
adjunto y devuélvela como JSON válido:

{
  "nombre": "Nombre completo del candidato",
  "telefono": "Número de teléfono",
  "email": "Correo electrónico",
  "habilidades": ["habilidad1", "habilidad2", "..."],
  "experiencia_anios": 0.0,
  "educacion": "Nivel de educación más alto",
  "resumen": "Resumen breve del perfil profesional",
  "confianza": 0.0
}

Donde:
- "habilidades" es un array de strings con las habilidades mencionadas
- "experiencia_anios" es el total de años de experiencia (número decimal)
- "confianza" es un valor entre 0.0 y 1.0 que indica qué tan confiable es la extracción

Solo devuelve el JSON, sin texto adicional."""


async def extract_cv_data(file_path: str) -> dict:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        uploaded_file = client.files.upload(file=str(path))
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[EXTRACTION_PROMPT, uploaded_file],
        )
    else:
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".heic": "image/heic",
        }
        mime_type = mime_types.get(suffix, "image/jpeg")

        with open(file_path, "rb") as f:
            image_bytes = f.read()

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[
                EXTRACTION_PROMPT,
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            ],
        )

    text = response.text
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    return json.loads(text.strip())
