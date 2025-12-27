
# PulseB2B Frontend (Vue.js + Bootstrap)

## Descripción
Este frontend ha sido migrado completamente a Vue.js (sin React), usando Vite para un desarrollo rápido y Bootstrap para una interfaz limpia, minimalista y elegante. La estructura sigue el patrón Modelo Vista Controlador (MVC) para facilitar el mantenimiento y la escalabilidad.

## Estructura del Proyecto

- `src/App.vue`: Vista principal. Implementa la gestión de tareas con Bootstrap y enlaza con el controlador.
- `src/controllers/TaskController.js`: Controlador de lógica de negocio para tareas (fetch, agregar, eliminar, alternar completado).
- `src/main.js`: Punto de entrada de la app Vue.
- `src/style.css`: Estilos personalizados mínimos (Bootstrap es la base visual).
- `index.html`: Incluye Bootstrap y monta la app Vue.

## Instalación y Uso

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

## Patrón MVC
- **Modelo**: Los datos de tareas se gestionan en el controlador (`TaskController.js`) usando `ref` de Vue.
- **Vista**: `App.vue` muestra la UI y responde a eventos del usuario.
- **Controlador**: `TaskController.js` expone métodos para manipular el modelo y es consumido por la vista.

## Integración Backend
- El controlador simula integración con backend usando fetch a una API pública.
- Puedes reemplazar la URL en `TaskController.js` para conectar con tu backend real.

## Personalización
- Agrega nuevas vistas en `src/components/` y nuevos controladores en `src/controllers/`.
- Usa clases de Bootstrap para mantener la coherencia visual.

## Limpieza
- Todo el código y vistas innecesarias han sido eliminados.
- El proyecto está listo para escalar o personalizar según tus necesidades.

---

¿Dudas o necesitas ejemplos de nuevas vistas/controladores? ¡Pide ayuda aquí!
