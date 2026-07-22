# PrismaVitae — Frontend

Este es el frontend para el proyecto **PrismaVitae**, una aplicación web diseñada para automatizar el escaneo de currículums mediante Inteligencia Artificial y gestionar tablas de datos para revisión de propuestas y reajustes salariales.

## 🚀 Stack Tecnológico

- **Framework:** React (inicializado con Vite)
- **Lenguaje:** TypeScript
- **Estilos y Componentes:** TailwindCSS (con Shadcn UI o Material UI)
- **Peticiones HTTP:** Axios o Fetch API
- **Enrutamiento:** React Router

## 📂 Arquitectura y Módulos Principales

La interfaz de usuario se divide en dos módulos principales:

### 1. Escáner de CVs
- **Pantalla de Carga:** Interfaz amigable para arrastrar y soltar (drag-and-drop) archivos PDF o tomar fotos. Incluye feedback visual durante el procesamiento de la IA.
- **Revisión y Edición:** Muestra un formulario pre-llenado con los datos extraídos (Nombre, Teléfono, Habilidades, etc.). Permite al usuario editar o corregir la información extraída por la IA antes de guardarla.
- **Lista de Candidatos:** Tabla general con todos los candidatos procesados y funcionalidad para exportar los datos a Excel.

### 2. Gestión de Tablas (Ruth Julio De Camps)
Una vista contenedora basada en pestañas (Tabs) para gestionar las hojas de datos:
- **Propuestas:** Tabla de visualización y formulario modal para agregar nuevos registros (con campos pre-llenados automáticamente).
- **Plantilla de Reajuste:** Tabla y formulario de edición que incluye **cálculos automáticos en vivo**. Al ingresar un salario actual y un salario solicitado, el frontend calcula automáticamente la diferencia salarial y el porcentaje de incremento.
- **No Proceden:** Tabla y formulario estándar para la gestión de casos que no aplican.

## ⚙️ Configuración y Ejecución Local

Para ejecutar el entorno de desarrollo localmente:

1. **Acceder al directorio del frontend:**
   ```bash
   cd frontend
   ```

2. **Instalar las dependencias:**
   ```bash
   npm install
   # o
   yarn install
   ```

3. **Iniciar el servidor de desarrollo:**
   ```bash
   npm run dev
   # o
   yarn dev
   ```
   La aplicación se abrirá por defecto en `http://localhost:5173`.

## 🔌 Integración y Despliegue

- **Desarrollo Local:** El frontend se comunica con los endpoints del backend (FastAPI). Asegúrate de que el backend tenga configurado CORS para aceptar peticiones de `localhost:5173`.
- **Producción:** 
  1. Construye la aplicación ejecutando `npm run build`.
  2. Los archivos estáticos generados en la carpeta `dist/` serán servidos directamente por FastAPI o tu servidor web (Nginx/Apache).
