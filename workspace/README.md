# PulseB2B Frontend (Vue.js + Bootstrap) + Backend (Python Flask)

## Descripción
Este proyecto ahora cuenta con un backend en Python (Flask) y un frontend en Vue.js (Vite + Bootstrap). La lógica de negocio de usuarios y tareas ha sido migrada a Python, exponiendo endpoints REST para consumo del frontend.

## Estructura del Proyecto

- `src/App.vue`: Vista principal. Implementa la gestión de tareas con Bootstrap y enlaza con el backend.
- `src/controllers/TaskController.js` y `src/controllers/UserController.js`: Controladores legacy (pueden eliminarse tras migración total a Python).
- `src/main.js`: Punto de entrada de la app Vue.
- `backend/app.py`: Servidor Flask con endpoints `/api/users` y `/api/tasks`.
- `backend/user_controller.py` y `backend/task_controller.py`: Lógica de negocio en Python.
- `index.html`: Incluye Bootstrap y monta la app Vue.

## Instalación y Uso

### Frontend
1. Instala dependencias:
    ```sh
    npm install
    ```
2. Ejecuta en modo desarrollo:
    ```sh
    npm run dev
    ```
3. Compila para producción:
    ```sh
    npm run build
    ```

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
- La lógica de negocio ahora reside en Python. Puedes extender los controladores en `backend/`.
- El frontend puede consumir los endpoints REST usando fetch/Axios.
- Elimina los controladores JS si ya no los necesitas.

---

¿Dudas o necesitas ejemplos de nuevas vistas/controladores en Python? ¡Pide ayuda aquí!
