# PulseB2B Frontend (HTML + Tailwind CSS) + Backend (Python Flask)

## Descripción
Este proyecto ahora cuenta con un backend en Python (Flask) y un frontend moderno basado únicamente en HTML y Tailwind CSS. Toda la lógica de negocio de usuarios y tareas reside en el backend Python, y el frontend es una SPA ligera sin frameworks JS.

## Estructura del Proyecto

- `index.html`: Vista principal, navegación y lógica de la app con Tailwind CSS y JavaScript vanilla.
- `src/style.css`: (opcional) Estilos personalizados mínimos.
- `backend/app.py`: Servidor Flask con endpoints `/api/users` y `/api/tasks`.
- `backend/user_controller.py` y `backend/task_controller.py`: Lógica de negocio en Python.

## Instalación y Uso

### Frontend
1. Abre `index.html` directamente en tu navegador. No requiere build ni dependencias.

### Backend (Python)
1. Instala dependencias:
    ```sh
    pip install flask requests
    ```
2. Ejecuta el servidor:
    ```sh
    python backend/app.py
    ```

## API REST
- `GET /api/users`: Lista usuarios.
- `GET /api/tasks`: Lista tareas.
- `POST /api/tasks`: Agrega tarea.
- `POST /api/tasks/<id>/toggle`: Alterna completado.
- `DELETE /api/tasks/<id>`: Elimina tarea.

## Migración y Personalización
- El frontend es HTML + Tailwind CSS, sin dependencias de Vue ni Bootstrap.
- El backend es Python Flask, puedes extender los controladores en `backend/`.
- Elimina cualquier referencia a controladores JS o archivos Vue.

---

¿Dudas o necesitas ejemplos de nuevas vistas/controladores en Python? ¡Pide ayuda aquí!
