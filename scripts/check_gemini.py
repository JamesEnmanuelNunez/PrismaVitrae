"""Prueba manual de extracción contra Gemini real (usa la API pagada).

Uso:
    uv run python scripts/check_gemini.py ruta/al/documento.pdf
    uv run python scripts/check_gemini.py ruta/al/archivo.jpg

Requiere GEMINI_API_KEY en .env. NO lo ejecuta pytest.
"""

import asyncio
import sys
from pathlib import Path

from app.services.ai_extractor import extract_document_data


async def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: uv run python scripts/check_gemini.py <archivo>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"No existe: {path}")
        sys.exit(1)

    data = await extract_document_data(str(path))
    print("Extracción:")
    for key, value in data.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())