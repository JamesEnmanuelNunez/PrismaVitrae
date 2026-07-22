# PrismaVitae — Backend FastAPI: Plan de Implementación Consolidado

Este plan consolida todas las fases necesarias para construir el backend del sistema **PrismaVitae**. El sistema manejará dos funcionalidades principales:
1. **Escáner Inteligente de CVs:** Extracción de datos con IA (Gemini) y almacenamiento de currículums.
2. **Gestión de Tablas (Ruth Julio De Camps):** Administración (CRUD) de propuestas, reajustes salariales y casos no procedentes.

> [!NOTE]
> Este plan está enfocado **exclusivamente en el backend**, utilizando FastAPI, SQLModel, Supabase (Storage + BD) y Google Gemini, respetando la skill configurada.

---

## Fase 1 — Setup del Proyecto y Arquitectura

### 1.1 Estructura de Directorios
Se mantendrá una arquitectura limpia y modular, orientada solo al backend:

```text
PrismaVitae/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point de FastAPI + CORS
│   ├── config.py               # Configuración (pydantic-settings)
│   ├── dependencies.py         # Dependencias inyectables (DB, Auth)
│   │
│   ├── models/                 # Modelos SQLModel (Tablas DB)
│   │   ├── __init__.py
│   │   ├── candidato.py
│   │   ├── propuesta.py
│   │   ├── reajuste.py
│   │   └── no_procede.py
│   │
│   ├── schemas/                # Schemas Pydantic (Request/Response)
│   │   └── ...                 
│   │
│   ├── routers/                # Controladores / Endpoints
│   │   ├── __init__.py
│   │   ├── scanner.py          # /escanear
│   │   ├── candidates.py       # CRUD Candidatos
│   │   ├── export.py           # /exportar-excel
│   │   ├── propuestas.py       # CRUD Propuestas
│   │   ├── reajustes.py        # CRUD Reajustes
│   │   └── no_proceden.py      # CRUD No Proceden
│   │
│   └── services/               # Lógica de Negocio
│       ├── __init__.py
│       ├── ai_extractor.py     # Gemini API
│       ├── supabase_storage.py # Storage
│       └── excel_generator.py  # openpyxl
│
├── tests/                      # Suite de tests
├── .env
└── pyproject.toml              # Dependencias (uv)
```

### 1.2 Inicialización y Dependencias
Se usará `uv` para instalar:
- `fastapi[standard]`, `pydantic-settings`, `sqlmodel`, `supabase`, `google-genai`, `openpyxl`, `httpx`, `python-multipart`.
- Herramientas de desarrollo: `ruff`, `pytest`, `pytest-asyncio`.

---

## Fase 2 — Base de Datos y Modelos (SQLModel)

Se configurarán todas las tablas en Supabase (PostgreSQL) y se reflejarán en SQLModel.

### 2.1 Modelo `Candidato` (Módulo CV)
- `id` (uuid, PK), `nombre`, `telefono`, `email`, `educacion`, `direccion`, `resumen`, `archivo_url`, `datos_crudos` (JSON), `confianza`.

### 2.2 Modelo `Propuesta` (Módulo Tablas R.J.C.)
- `id` (uuid, PK), `no` (int), `reg_dist`, `cedula`, `nombre_completo`, `sexo`, `cargo_solicitado`, `escolaridad`, `en_sustitucion_de`, `cedula_no`, `fecha_ingreso`, `centro`, `referido_por`, `telefono`.

### 2.3 Modelo `Reajuste` (Módulo Tablas R.J.C.)
- `id` (uuid, PK), `cedula`, `nombre_completo`, `grupo_ocupacional`, `cargo`, `salario_actual` (float), `salario_solicitado` (float), `observacion`, `diferencia_salarial` (float), `porcentaje_incremento` (float), `fecha_efectividad`.

### 2.4 Modelo `NoProcede` (Módulo Tablas R.J.C.)
- `id` (uuid, PK), `no` (int), `reg_dist`, `cedula`, `nombre_completo`, `sexo`, `cargo_solicitado`, `salario_solicitado` (float), `escolaridad`, `observacion`, `referido_por`, `telefono`.
7
---

## Fase 3 — Servicios y Lógica Central

### 3.1 Servicio de IA (`services/ai_extractor.py`)
- Integración con **Google Gemini** para recibir el documento (PDF/Imagen) y devolver un JSON estructurado con los datos del candidato y un score de `confianza`.

### 3.2 Servicio de Storage (`services/supabase_storage.py`)
- Subida de archivos (`upload_file`) al bucket de Supabase y obtención de la URL pública.
- Eliminación de archivos vinculados a candidatos borrados (`delete_file`).

### 3.3 Servicio de Exportación Excel (`services/excel_generator.py`)
- Creación de `.xlsx` con `openpyxl` a partir de los datos de la base de datos (tanto para exportar la tabla de Candidatos como, opcionalmente, las otras tablas).

---

## Fase 4 — Endpoints y Routers

### 4.1 Endpoints del Escáner de CV
- `POST /api/escanear`: Recibe archivo (`multipart/form-data`), lo sube a Storage, envía a Gemini, guarda en BD y devuelve JSON de extracción.
- `GET /api/exportar-excel`: Genera y descarga el archivo `.xlsx` de candidatos.

### 4.2 Endpoints CRUD (Operaciones de Tabla)
Para cada uno de los recursos (`candidatos`, `propuestas`, `reajustes`, `no_proceden`), se crearán las mismas rutas estandarizadas:

- `GET /api/{recurso}/`: Listar registros (con paginación).
- `POST /api/{recurso}/`: Crear registro.
- `GET /api/{recurso}/{id}`: Leer detalle.
- `PUT /api/{recurso}/{id}`: Actualizar.
- `DELETE /api/{recurso}/{id}`: Eliminar.

---

## Fase 5 — Pruebas y Validación (Testing)

- Configuración de `pytest`.
- **Mocks:** Simular llamadas a Gemini y a Supabase para evitar costos y latencia durante pruebas.
- **Tests Críticos:**
  1. Extracción de datos (`POST /escanear`).
  2. Subida de archivos no permitidos (validación 422).
  3. Operaciones CRUD básicas (crear, leer, actualizar, borrar) para Propuestas y Reajustes.
  4. Generación de Excel.

---

## Orden de Ejecución Paso a Paso

Sigue este orden estrictamente para la implementación:

| Paso | Módulo | Descripción de Tarea |
|------|--------|----------------------|
| **1** | Setup | `uv init`, instalación de dependencias, configuración de `.env`, `config.py` y `main.py` con CORS. |
| **2** | Base de Datos | Configuración del motor de SQLModel y conexión a PostgreSQL (Supabase). |
| **3** | Modelos | Creación de todos los archivos en `models/` (Candidato, Propuesta, Reajuste, NoProcede) y `schemas/`. |
| **4** | Servicios | Implementación de `ai_extractor.py` (Gemini) y `supabase_storage.py` (Bucket). |
| **5** | Escáner | Implementación de `routers/scanner.py` (`POST /escanear`). |
| **6** | CRUD CVs | Implementación de `routers/candidates.py`. |
| **7** | Exportación | Implementación de `excel_generator.py` y `routers/export.py`. |
| **8** | CRUD Tablas | Implementación de `routers/propuestas.py`, `routers/reajustes.py`, `routers/no_proceden.py`. |
| **9** | Testing | Escritura de tests con Pytest y validación final. |
