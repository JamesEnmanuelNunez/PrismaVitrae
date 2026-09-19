# PrismaVitae — Backend

Backend FastAPI para el sistema PrismaVitae: escáner de documentos con IA (CVs y cédulas dominicanas) y gestión de tablas operativas de Recursos Humanos (Propuestas, Reajustes salariales, No Proceden).

## Stack

- **FastAPI** (`app.main:app`)
- **Supabase**: PostgREST (BD), Storage (bucket `cvs`) y Auth
- **Google Gemini**: extracción estructurada de datos de documentos
- **openpyxl**: exportación a Excel
- **uv** como gestor de dependencias, **ruff** como linter, **pytest** para tests

## Setup

```bash
uv sync                 # instala dependencias (incluye dev)
cp .env.example .env    # y completa las credenciales
uv run fastapi dev      # servidor de desarrollo (entrypoint en pyproject.toml)
```

Variables de entorno necesarias (ver `.env.example`):

- `SUPABASE_URL`, `SUPABASE_KEY` (anon), `SUPABASE_SERVICE_KEY` (solo scripts de admin)
- `GEMINI_API_KEY`
- `GEMINI_MODEL` (default `gemini-3.5-flash`)
- `CORS_ORIGINS` (lista JSON de orígenes permitidos)

## Tests

```bash
uv run pytest
```

La suite corre contra **Supabase real** (usa las credenciales de `.env`). Por eso:

- Cada test usa datos únicos (sufijos `uuid`) y **se auto-limpia** al terminar (`tests/conftest.py`), tanto filas de tablas como usuarios de Auth creados en `register`.
- Los tests de auth (register/login) requieren una **`SUPABASE_SERVICE_KEY` real** (service_role, no anon): sin ella se **saltan** para no ensuciar Auth ni fallar por permisos.
- Ten en cuenta que Supabase limita los signups por hora (rate limit); los tests de registro pueden fallar esporádicamente con 429 hasta que se resetee.

Nota: los tests apuntan a la BD de desarrollo/producción. Si quieres una suite offline/hermética, ese es un cambio de arquitectura aparte.

## Scripts

- `scripts/create_admin.py` — promueve un usuario existente a admin (usa `SUPABASE_SERVICE_KEY`). Útil para el primer usuario tras restaurar el flujo de aprobación. Ejecutar con `uv run python -m scripts.create_admin <email>`.
- `scripts/list_users.py` — lista los correos registrados. Ejecutar con `uv run python -m scripts.list_users`.
- `scripts/check_gemini.py` — prueba manual de extracción contra Gemini real (no lo ejecuta pytest). Ejecutar con `uv run python -m scripts.check_gemini <archivo>`.

## Base de datos

El esquema de Supabase está en `db/schema.sql` (tablas, RLS, bucket de storage). Se aplica manualmente desde el SQL Editor de Supabase.

## Estructura

```
app/
  main.py           # App FastAPI, CORS, logging, handlers de error
  config.py         # Settings (pydantic-settings)
  dependencies.py   # Cliente Supabase singleton + dependencias de auth
  routers/          # Capa HTTP (auth, scanner, CRUD por tabla, export)
  services/         # Lógica de negocio (IA, storage, Excel, auth, repositorio CRUD)
  schemas/          # DTOs Pydantic
db/schema.sql       # DDL de Supabase
scripts/            # Utilidades de mantenimiento
tests/              # Suite pytest (online contra Supabase real)
```