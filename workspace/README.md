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
│   └── style.css (Tailwind personalizado)
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
3. El diseño utiliza Tailwind CSS puro, sin frameworks JS. Todas las vistas y componentes son HTML + Tailwind.

## Vistas y Experiencia de Usuario

### Panel Free: Plan & Services Management (`/dashboard/billing-plans`)

**Estrategia UX/UI: The Freemium Mirror**

La interfaz se divide en dos zonas visuales contrastantes:

- **Zona de Valor Actual (Free):**
  - Fondo y tarjetas en tonos Zinc/Slate (grises tenues, Tailwind: zinc-100/slate-200).
  - Mensaje destacado: “Ahorro de tiempo básico”.
  - Servicios activos para el usuario Free, cada uno en una tarjeta clara y minimalista.
  - Servicios Free:
    - **Daily Telegram Signal:** 1 lead de alta intención por día entregado a tu teléfono. Valor: Conciencia instantánea de oportunidades top sin esfuerzo.
    - **Current Weekly Radar:** Acceso al reporte PDF de inteligencia de la semana actual. Valor: Visión estratégica de las últimas rondas de inversión en tu región.
    - **Dashboard Preview:** Acceso limitado a la tabla global de leads (info de contacto difuminada). Valor: Vista en tiempo real del volumen de mercado y tendencias de stack tecnológico.

- **Zona de Valor Bloqueado (Pro/Enterprise):**
  - Fondo y tarjetas en tonos Indigo (Tailwind: indigo-600/700) con efectos glow sutiles y candados elegantes.
  - Mensaje destacado: “Dominio del mercado”.
  - Muestra los servicios premium bloqueados, con descripciones y CTA para actualizar.

---

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

## Guía de Despliegue y Pruebas

### Despliegue Local

#### Backend (Flask)
1. Instala Python 3.9+ y pip si no los tienes.
2. Ve a la carpeta `backend`:
    ```sh
    cd backend
    pip install flask requests
    ```
3. Ejecuta el servidor:
    ```sh
    python app.py
    ```
   El backend estará disponible en http://127.0.0.1:5000

#### Frontend
1. Ve a la raíz del proyecto.
2. Abre `index.html` directamente en tu navegador (doble clic o "Abrir con...").
3. El frontend se conectará automáticamente al backend Flask en http://127.0.0.1:5000/api

### Pruebas Manuales

- **Tareas:**
  - Agrega, elimina y alterna tareas desde la interfaz.
  - Verifica que los cambios se reflejan tras recargar la página (persistencia depende de la API backend).
  - Si el backend no está disponible, verás mensajes de error.
- **Usuarios:**
  - Agrega usuarios desde la interfaz y verifica que aparecen en la tabla.
  - Si el backend no responde, verás mensajes de error.
- **Feedback visual:**
  - Observa los mensajes de "Cargando..." y errores si hay problemas de red o backend.

### Pruebas de API (opcional)
Puedes probar los endpoints directamente con herramientas como Postman o curl:

- Listar tareas:
  ```sh
  curl http://127.0.0.1:5000/api/tasks
  ```
- Agregar tarea:
  ```sh
  curl -X POST -H "Content-Type: application/json" -d '{"title":"Nueva tarea"}' http://127.0.0.1:5000/api/tasks
  ```
- Alternar tarea:
  ```sh
  curl -X POST http://127.0.0.1:5000/api/tasks/1/toggle
  ```
- Eliminar tarea:
  ```sh
  curl -X DELETE http://127.0.0.1:5000/api/tasks/1
  ```

### Despliegue en Producción

- **Backend:**
  - Usa un servidor WSGI como Gunicorn o uWSGI para producción.
  - Configura un proxy inverso (Nginx, Apache) si es necesario.
- **Frontend:**
  - Sube los archivos estáticos (`index.html`, `src/`) a un servidor web (Nginx, Apache, Netlify, Vercel, etc).
  - Asegúrate de que el frontend apunte a la URL correcta del backend en producción (ajusta `API_URL` en `model.js`).

---

¿Dudas o necesitas ejemplos de nuevas vistas/controladores en Python o estructura MVC? ¡Pide ayuda aquí!
