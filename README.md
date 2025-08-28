# Proyecto Abogados Forenses

Este repositorio contiene el código fuente para la aplicación web de Abogados Forenses, que consta de dos partes principales:

1.  **Frontend Público (`frontend/`)**: El sitio web corporativo para Abogados Forenses, diseñado para la presencia online y la captación de clientes.
2.  **Backend y Dashboard (`backend/`)**: Un sistema de gestión interno (ForensicWeb) para abogados, que incluye funcionalidades de dashboard, gestión de casos, clientes, equipos, agenda y estadísticas.

## Estructura del Repositorio

```
proyecto-abogados-forenses/
├── frontend/                    # Sitio web público (abogadosforenses.org)
│   ├── index.html
│   ├── servicios.html
│   ├── blog.html
│   ├── contacto.html
│   ├── css/
│   ├── js/
│   └── images/                  # (Pendiente de añadir)
├── backend/                     # API Flask y Dashboard interno (ForensicWeb)
│   ├── venv/
│   ├── src/
│   │   ├── models/              # Modelos de base de datos
│   │   ├── routes/              # Endpoints de la API
│   │   ├── static/              # Archivos estáticos del dashboard (HTML, CSS, JS)
│   │   ├── main.py              # Punto de entrada de la aplicación Flask
│   │   └── database/
│   │       └── app.db           # Base de datos SQLite (desarrollo)
│   └── requirements.txt         # Dependencias de Python
├── docs/                        # Documentación adicional (API, despliegue)
│   ├── api_documentation.md     # (Pendiente de crear)
│   └── deployment_guide.md      # (Pendiente de crear)
└── README.md
```

## Configuración y Ejecución Local

### 1. Backend (API Flask y Dashboard)

El backend es una aplicación Flask que sirve la API REST y los archivos estáticos del dashboard.

**Requisitos:**
- Python 3.8+
- pip

**Pasos:**

1.  **Navegar al directorio del backend:**
    ```bash
    cd backend
    ```

2.  **Crear y activar el entorno virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación Flask:**
    ```bash
    python src/main.py
    ```
    El servidor se iniciará en `http://127.0.0.1:5001` (o el puerto configurado en `src/main.py`).

    **Credenciales de prueba para el dashboard:**
    - **Email:** `admin@forensicweb.com`
    - **Contraseña:** `admin123`

### 2. Frontend Público

El frontend público es un sitio web estático. Puedes abrir los archivos HTML directamente en tu navegador o usar un servidor web local (como `live-server` de Node.js o el módulo `http.server` de Python).

**Pasos (usando Python):**

1.  **Navegar al directorio del frontend:**
    ```bash
    cd frontend
    ```

2.  **Iniciar un servidor HTTP simple:**
    ```bash
    python3 -m http.server 8000
    ```
    Luego, abre tu navegador y ve a `http://localhost:8000`.

## Despliegue

### Backend (API Flask)

Para el despliegue en producción, se recomienda usar un servicio de hosting que soporte aplicaciones Python/Flask, como Heroku, Railway, Render, o un VPS. Deberás configurar variables de entorno para la base de datos (PostgreSQL recomendado) y la clave secreta.

### Frontend Público

El frontend es un sitio estático y puede ser desplegado fácilmente en servicios como GitHub Pages, Netlify, Vercel, o cualquier servidor web estático.

## Contribución

¡Las contribuciones son bienvenidas! Por favor, sigue los siguientes pasos:

1.  Haz un fork del repositorio.
2.  Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3.  Realiza tus cambios y haz commit (`git commit -m "feat: Añadir nueva funcionalidad X"`).
4.  Haz push a la rama (`git push origin feature/nueva-funcionalidad`).
5.  Abre un Pull Request.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles. (Pendiente de crear)


