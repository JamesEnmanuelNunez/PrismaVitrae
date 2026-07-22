# PrismaVitae — Frontend: Plan de Implementación

Este plan detalla la construcción de la interfaz de usuario para **PrismaVitae**, cubriendo tanto el módulo original de escaneo de currículums como el nuevo módulo de gestión de tablas (Ruth Julio De Camps).

## 1. Stack Tecnológico
- **Framework:** React (usando Vite para web o Expo si se decide empaquetar como app móvil nativa).
- **Lenguaje:** TypeScript.
- **Componentes UI:** Shadcn UI, Material UI, o TailwindCSS puro.
- **Conexión al Backend:** Axios o Fetch API apuntando a la API de FastAPI.

---

## 2. Arquitectura de Pantallas (Rutas)

### 2.1 Módulo: Escáner de CVs
1. **Pantalla de Carga (Upload):** 
   - Interfaz para arrastrar/soltar un archivo PDF o tomar una foto.
   - Botón de "Escanear CV". Envía un `POST /api/escanear`.
   - Indicador de carga (spinner) mientras la IA procesa el documento.
2. **Pantalla de Revisión:** 
   - Muestra un formulario pre-llenado con los datos extraídos (Nombre, Teléfono, Habilidades, etc.).
   - Permite al usuario editar los campos si la IA cometió algún error.
   - Botón "Guardar Candidato".
3. **Pantalla de Lista de Candidatos:**
   - Tabla con todos los candidatos procesados consumiendo `GET /api/candidatos/`.
   - Botón de "Exportar a Excel" que descarga el archivo desde `GET /api/exportar-excel`.

### 2.2 Módulo: Gestión de Tablas (Ruth Julio De Camps)
Se creará una vista contenedora con **Pestañas (Tabs)** para alternar entre las tres hojas del archivo Excel original.

#### Pestaña 1: Propuestas
- Tabla que consume `GET /api/propuestas/`.
- Botón "Agregar Nuevo" que abre un modal con el formulario.
- Campo `cargo_solicitado` pre-llenado con "TECNICO FACILITADOR ACOMPAÑANTE".

#### Pestaña 2: Plantilla de Reajuste
- Tabla que consume `GET /api/reajustes/`.
- Formulario de edición con **Campos Calculados Automáticos**:
  - Al escribir `salario_actual` y `salario_solicitado`, el frontend debe calcular automáticamente la `diferencia_salarial` (solicitado - actual).
  - El frontend también debe calcular y mostrar el `porcentaje_incremento`.

#### Pestaña 3: No Proceden
- Tabla que consume `GET /api/no_proceden/`.
- Formulario con campos estándar correspondientes al modelo.

---

## 3. Integración con el Backend (FastAPI)

- **CORS:** El frontend en desarrollo correrá en `http://localhost:5173`. El backend debe tener este origin permitido en su configuración CORS.
- **Despliegue a Producción:** Una vez que el frontend esté terminado, se ejecutará el comando `npm run build` o `yarn build`. La carpeta estática generada (`dist/`) se colocará en el servidor y FastAPI se encargará de servirla utilizando:
  ```python
  app.frontend("/", directory="frontend/dist")
  ```

---

## 4. Orden de Ejecución Sugerido para el Frontend

1. `npm create vite@latest frontend -- --template react-ts` (Inicializar proyecto).
2. Instalar dependencias (TailwindCSS, React Router, Axios, Lucide Icons).
3. Configurar React Router para las dos secciones principales (Escáner vs. Tablas).
4. Crear componentes UI base (Botones, Inputs, Modales, Pestañas).
5. Implementar el módulo de carga de CV y vista previa de extracción.
6. Implementar el módulo de las 3 tablas de Excel con sus respectivos formularios y validaciones en vivo (cálculos salariales).
7. Conectar todo con los endpoints del backend en FastAPI.
