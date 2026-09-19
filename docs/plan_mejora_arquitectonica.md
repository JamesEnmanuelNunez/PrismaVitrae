# Plan de Mejora Arquitectónica — PrismaVitae Backend

> Creado: 2026-09-18
> Estado: **Ejecutado** (2026-09-18)

Basado en un análisis exhaustivo del repositorio, este plan organiza todas las mejoras en fases ordenadas por prioridad: primero lo que está roto, luego la basura, después las redundancias y finalmente las mejoras de arquitectura.

---

## Fase 1 — Correcciones Críticas (lo que está roto)

### 1.1 Corregir `pytest` que no arranca

> ⚠️ Actualmente `uv run pytest` falla de inmediato con `ModuleNotFoundError: No module named 'app'` porque falta configurar el `pythonpath`.

**Archivo:** `pyproject.toml`

Agregar `pythonpath = ["."]` dentro de `[tool.pytest.ini_options]`:

```diff
 [tool.pytest.ini_options]
 asyncio_mode = "auto"
+pythonpath = ["."]
```

### 1.2 Corregir forward reference en schema de auth

> ⚠️ En `app/schemas/auth.py`, `AuthResponse` (línea 15) referencia `UserResponse` (línea 21) antes de que esté definida. Funciona por lazy evaluation de Pydantic, pero es frágil y confuso.

**Archivo:** `app/schemas/auth.py`

Reordenar las clases para que `UserResponse` se defina **antes** de `AuthResponse`.

---

## Fase 2 — Eliminar Archivos Basura y Residuales

### 2.1 Archivo lock temporal de LibreOffice

**[ELIMINAR]** `.~lock.RUTH JULIO DE CAMPS 08-12-2025.xlsx#`
- Archivo temporal huérfano de LibreOffice. Ya está marcado como `deleted` en el staging de git, pero sigue físicamente en disco.

### 2.2 Documentación del frontend en el repo del backend

**[ELIMINAR]** `README_FRONTEND.md`
- Documentación completa del frontend (React/Vite/TailwindCSS). Este repositorio es exclusivamente backend; el frontend vive en `PrismaVitae FRONTEND/`.

**[ELIMINAR]** `docs/plan_frontend.md`
- Plan de especificación del frontend guardado dentro del repo del backend.

### 2.3 Artefacto de planificación obsoleto

**[ELIMINAR]** `docs/cedulacv.md`
- Artefacto residual de una sesión anterior de un agente IA. Contiene instrucciones con "*dale a Proceed*" y hace referencia a columnas de BD que nunca se crearon. La funcionalidad que describe ya está implementada en `app/routers/scanner.py`.

### 2.4 Plan del backend desactualizado

**[ELIMINAR]** `docs/plan_backend.md`
- Hace referencia a `app/models/` y SQLModel, que ya fueron eliminados. La arquitectura real ya está documentada en el `README.md`.

### 2.5 Limpiar directorios `__pycache__`

- Borrar todos los directorios `__pycache__/` existentes en el árbol: `app/`, `app/schemas/`, `app/routers/`, `app/services/`, `tests/`.

---

## Fase 3 — Eliminar Código Muerto

### 3.1 Funciones no utilizadas en el scanner

**Archivo:** `app/routers/scanner.py`

Eliminar `extract_first_name()` (líneas 35–37) y `extract_first_last_name()` (líneas 40–42). Nadie las invoca. La función `_matches_candidato()` implementa su propia lógica de partición de nombres internamente.

### 3.2 Excepciones huérfanas

**Archivo:** `app/exceptions.py`

Las siguientes excepciones están definidas pero **nunca se lanzan** en ningún módulo:

| Excepción | Status | ¿Se usa? |
|:---|:---|:---|
| `PrismaVitaeError` | 400 | ✅ Base del handler |
| `NotFoundError` | 404 | ✅ Usada en `crud.py` |
| `ExtractionError` | 500 | ✅ Usada en `ai_extractor.py` |
| `AuthError` | 401 | ❌ Nunca se lanza |
| `ForbiddenError` | 403 | ❌ Nunca se lanza |
| `ValidationError` | 422 | ❌ Nunca se lanza |
| `StorageError` | 500 | ❌ Nunca se lanza |

**Decisión pendiente:** Mantenerlas y adoptarlas progresivamente (ver Fase 5.2) o eliminarlas por ahora.

---

## Fase 4 — Centralizar Redundancias (DRY)

### 4.1 Lista de permisos de admin triplicada

La misma lista de 10 permisos está definida en 3 sitios:

| Ubicación | Variable |
|:---|:---|
| `app/services/auth.py:13-17` | `DEFAULT_PERMISSIONS["admin"]` |
| `scripts/create_admin.py:18-29` | `ADMIN_PERMISSIONS` |
| `tests/conftest.py:19-30` | `MOCK_USER.permissions` |

**Cambios:**
- `scripts/create_admin.py` → importar `from app.services.auth import DEFAULT_PERMISSIONS` y usar `DEFAULT_PERMISSIONS["admin"]`.
- `tests/conftest.py` → importar `from app.services.auth import DEFAULT_PERMISSIONS` y usar `DEFAULT_PERMISSIONS["admin"]`.

### 4.2 Mapeo de tipos MIME triplicado con discrepancias

Tres diccionarios extensión→MIME type en tres archivos distintos:

| Archivo | Variable | Incluye `.heic`? |
|:---|:---|:---|
| `app/routers/scanner.py:16` | `ALLOWED_TYPES` | ❌ |
| `app/services/supabase_storage.py:10` | `MIME_TYPES` | ❌ |
| `app/services/ai_extractor.py:16` | `IMAGE_MIME_TYPES` | ✅ |

**Cambios:**
- **[NUEVO]** `app/constants.py`: definir un único diccionario `ALLOWED_MIME_TYPES`.
- Modificar los tres archivos para importar desde `app.constants`.

### 4.3 Paginación manual repetida (patrón `while True` + `range`)

Mismo patrón de paginación PostgREST implementado en 3 sitios:
- `app/routers/export.py:25-42` — `_fetch_all_rows()`
- `app/routers/scanner.py:73-89` — `find_matching_candidato()`
- `tests/conftest.py:72-83` — `list_all()`

**Cambios:**
- Agregar un método `list_all()` a `TableRepository` en `app/services/crud.py`.
- Refactorizar `export.py` y `scanner.py` para usar el nuevo método.

### 4.4 Función de resolución de usuario duplicada en dependencies

**Archivo:** `app/dependencies.py`

- `_resolve_user()` y `get_current_user_dep()` son idénticas en comportamiento. Eliminar `_resolve_user` y usar `get_current_user_dep` directamente.
- En `require_permission()`: cambiar la dependencia interna `_check(db, token)` para inyectar `user: AuthDep` directamente, evitando resolver el usuario una segunda vez.

---

## Fase 5 — Mejoras Arquitectónicas

### 5.1 Simplificar registro de routers en `main.py`

**Archivo:** `app/main.py`

Actualmente se repite 7 veces `app.include_router(..., prefix="/api")`.

```python
# Después (limpio):
for router in [auth_router, scanner_router, export_router,
               candidates_router, propuestas_router,
               reajustes_router, no_proceden_router]:
    app.include_router(router, prefix="/api")
```

### 5.2 Adoptar excepciones de dominio en lugar de `HTTPException`

Actualmente el código mezcla dos patrones de error incompatibles:
- `PrismaVitaeError` → manejado por el handler global en `main.py`
- `HTTPException` → manejado por FastAPI/Starlette directamente

**Archivos afectados:**
- `app/services/auth.py` → reemplazar `raise ValueError(...)` por `raise AuthError(...)` o `raise ForbiddenError(...)`.
- `app/routers/auth.py` → eliminar los bloques `try/except` repetitivos (6 endpoints) ya que el handler global se encargará.
- `app/dependencies.py` → reemplazar `HTTPException(401)` por `AuthError(...)` y `HTTPException(403)` por `ForbiddenError(...)`.
- `app/services/crud.py` → reemplazar `HTTPException(400)` por `PrismaVitaeError(...)`.

### 5.3 Formalizar scripts

**Archivos:** `scripts/list_users.py`, `scripts/create_admin.py`

Ambos scripts importan `dotenv` manualmente y leen `os.environ`. Refactorizar para importar `from app.config import settings`.

### 5.4 Corregir README inconsistente

**Archivo:** `README.md`

- Dice `tests/ # Suite pytest (offline)` pero los tests son **online** contra Supabase real. Corregir.
- Dice `uv run uvicorn app.main:app --reload` pero el `pyproject.toml` ya tiene `[tool.fastapi]` configurado, así que el comando recomendado es `uv run fastapi dev`.

---

## Fase 6 — Mejoras Opcionales (menor prioridad)

### 6.1 Reducir boilerplate del generador Excel

`app/services/excel_generator.py` (218 líneas): las 4 funciones de generación comparten ~80% de su estructura. Crear una función base genérica que reduzca el archivo a ~120 líneas.

### 6.2 Verificar permisos de lectura en endpoints GET

En `app/services/crud.py`, los endpoints `GET /` y `GET /{id}` solo verifican autenticación (`AuthDep`) pero no chequean los permisos de lectura específicos (`ver_candidatos`, `ver_propuestas`, etc.). Si deben ser enforceados, agregar un parámetro `read_permission` a `build_crud_router`.

---

## Orden de Ejecución Recomendado

| Paso | Fase | Descripción | Riesgo |
|:---:|:---|:---|:---|
| 1 | 1.1 | Corregir `pyproject.toml` para pytest | Ninguno |
| 2 | 1.2 | Reordenar clases en `auth.py` schema | Ninguno |
| 3 | 2.x | Eliminar archivos basura + limpiar `__pycache__` | Ninguno |
| 4 | 3.1 | Eliminar funciones muertas en `scanner.py` | Ninguno |
| 5 | 4.1 | Centralizar permisos de admin | Bajo |
| 6 | 4.2 | Unificar tipos MIME en `constants.py` | Bajo |
| 7 | 4.3 | Centralizar paginación en `TableRepository` | Bajo |
| 8 | 4.4 | Simplificar `dependencies.py` | Bajo |
| 9 | 5.1 | Simplificar registro de routers | Ninguno |
| 10 | 5.2 | Adoptar excepciones de dominio | Medio |
| 11 | 5.3 | Formalizar scripts | Bajo |
| 12 | 5.4 | Corregir README | Ninguno |
| 13 | 6.x | Mejoras opcionales | Bajo |

---

## Historial de Documentación Reemplazada

Los siguientes archivos de documentación serán eliminados como parte de la Fase 2 de este plan. Se registra aquí su contenido y propósito original:

| Archivo eliminado | Contenido original | Razón de eliminación |
|:---|:---|:---|
| `docs/plan_backend.md` | Plan de implementación del backend (6 fases). Hacía referencia a `app/models/` y SQLModel. | Desactualizado: la arquitectura cambió a Supabase PostgREST directo + `app/services/crud.py`. Reemplazado por el `README.md` actual y este plan. |
| `docs/plan_frontend.md` | Plan de especificación del frontend (React/Vite/TailwindCSS). | Pertenece al repositorio del frontend (`PrismaVitae FRONTEND/`), no al backend. |
| `docs/cedulacv.md` | Plan de implementación para fusión CV+Cédula generado por un agente IA. | Artefacto residual de sesión anterior. La funcionalidad ya está implementada en `app/routers/scanner.py`. |
| `README_FRONTEND.md` | Documentación de setup y módulos del frontend. | Pertenece al repositorio del frontend, no al backend. |
