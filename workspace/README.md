# PulseB2B (MVC: HTML + Tailwind CSS + Python Flask)

## Resumen de Cambios y Arquitectura

- **Frontend HTML + Tailwind CSS + MVC:**
  - Estructura Modelo Vista Controlador (MVC):
    - `src/model.js`: gestiona el estado y la comunicación con la API Flask.
    - `src/view.js`: renderiza datos, feedback de carga y errores en el DOM.
    - `src/controller.js`: conecta modelo y vista, maneja eventos y lógica de interacción.
  - Feedback visual de carga y errores para tareas y usuarios.
  - El frontend es una SPA ligera, sin frameworks JS ni Node/npm.
  - Navegación y vistas gestionadas en `index.html`.

- **Backend Python Flask con MVC:**
  - Estructura clara por Modelo, Vista y Controlador:
    - `backend/models/`: entidades de dominio (`user.py`, `task.py`).
    - `backend/controllers/`: lógica de negocio (`user_controller.py`, `task_controller.py`).
    - `backend/views/`: rutas y respuestas API (`api.py`).
    - `backend/app.py`: instancia la app y registra el blueprint de vistas.

- **Node/npm deprecados:**
  - Eliminados todos los archivos y dependencias de Node/npm y Vue.

## Estructura del Proyecto

```
workspace/
├── backend/
│   ├── app.py
│   ├── models/
│   │   ├── user.py
│   │   └── task.py
│   ├── controllers/
│   │   ├── user_controller.py
│   │   └── task_controller.py
│   └── views/
│       └── api.py
├── src/
│   ├── model.js
│   ├── view.js
│   └── controller.js
├── index.html
└── src/style.css (opcional)
```

## Instalación y Uso

### Backend (Python)
1. Instala dependencias:
    ```sh
    pip install flask requests
    ```
2. Ejecuta el servidor:
    ```sh
    python backend/app.py
    ```

### Frontend
1. Abre `index.html` directamente en tu navegador. No requiere build ni dependencias.
2. El frontend se conecta automáticamente a la API Flask en `http://127.0.0.1:5000/api`.

## API REST
- `GET /api/users`: Lista usuarios.
- `POST /api/users`: Agrega usuario.
- `GET /api/tasks`: Lista tareas.
- `POST /api/tasks`: Agrega tarea.
- `POST /api/tasks/<id>/toggle`: Alterna completado.
- `DELETE /api/tasks/<id>`: Elimina tarea.

## Migración y Personalización
- El frontend y backend siguen el patrón MVC para mayor claridad y escalabilidad.
- El backend es Python Flask, puedes extender los modelos, controladores y vistas en `backend/`.
- El frontend es modular, fácil de mantener y muestra feedback visual al usuario.

---

¿Dudas o necesitas ejemplos de nuevas vistas/controladores en Python o estructura MVC? ¡Pide ayuda aquí!
