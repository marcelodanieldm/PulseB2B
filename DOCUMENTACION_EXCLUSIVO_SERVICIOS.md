# PulseB2B: Documentación de Acceso Exclusivo, Servicios y Automatización

## 1. Acceso Exclusivo de Usuario

- **Login:**
  - Página de inicio de sesión minimalista (usuario y contraseña, o Google).
  - Validación contra Supabase Auth.
  - Si el usuario no está autenticado, no puede acceder a rutas protegidas.

- **Protección de rutas:**
  - Las rutas #dashboard, #radar, #settings-api y #exclusive-dashboard requieren autenticación.
  - Si el usuario no está autenticado y navega a una ruta protegida, es redirigido a #login.

## 2. Dashboard Exclusivo de Usuario

- **Sección SPA:**
  - Ruta: `#exclusive-dashboard`.
  - Solo visible para usuarios autenticados.
  - Muestra todos los servicios disponibles:
    - Servicios contratados: muestra detalles completos y acceso directo.
    - Servicios no contratados: muestra opción de "Upgrade".
  - Botón de desuscribirse para cada servicio contratado.
  - Botón de logout para cerrar sesión.

- **Servicios:**
  - Definidos en el frontend (ALL_SERVICES), pero el estado de contratación se obtiene de Supabase.
  - La columna `services` en la tabla `profiles` (Supabase) almacena un array de IDs de servicios contratados por el usuario.

- **Upgrade y Desuscripción:**
  - Al hacer upgrade, se agrega el servicio al array `services` en Supabase.
  - Al desuscribirse, se elimina el servicio del array en Supabase.
  - Los cambios se reflejan en tiempo real en la UI.

## 3. Integración con Supabase

- **Autenticación:**
  - Se utiliza Supabase Auth para login y logout.
- **Gestión de servicios:**
  - Se consulta y actualiza la columna `services` de la tabla `profiles` para cada usuario.
  - Ejemplo de estructura en Supabase:
    - Tabla: `profiles`
    - Columnas relevantes: `id` (UUID del usuario), `services` (array de texto)

## 4. GitHub Actions y Automatización

- **Workflows:**
  - Los jobs de GitHub Actions se ejecutan automáticamente al hacer push o pull request.
  - Puedes ver el estado de los jobs en la pestaña "Actions" de tu repositorio en GitHub.

- **Cómo probar los jobs:**
  - Realiza un commit y push de tus cambios.
  - Los workflows definidos en `.github/workflows/` se ejecutarán según su configuración (por ejemplo, en push a main o en PR).

## 5. Estructura de Archivos Clave

- `index.html`: Contiene toda la lógica SPA, login, dashboard exclusivo, integración con Supabase y lógica de servicios.
- `.github/workflows/`: Contiene los archivos de configuración de GitHub Actions para CI/CD y automatización.

## 6. Personalización y Extensión

- Puedes agregar más servicios editando el array `ALL_SERVICES` en el frontend y asegurándote de que los IDs coincidan con los almacenados en Supabase.
- Para agregar lógica de pago real, conecta el botón de upgrade a tu pasarela de pago y actualiza el backend tras el pago exitoso.

## 7. Seguridad

- Todas las rutas críticas están protegidas por autenticación.
- El usuario solo puede ver y gestionar sus propios servicios.
- El logout limpia el estado de autenticación y redirige a login.

---

**Última actualización:** 27 de diciembre de 2025
