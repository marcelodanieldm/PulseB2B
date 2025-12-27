# Migración a Frontend Bootstrap Puro

## Resumen
Se eliminó completamente el framework Vue.js y todas sus dependencias, migrando el frontend a una versión mínima y rápida basada únicamente en HTML y Bootstrap. Ahora la interfaz funciona sin ningún framework JavaScript ni herramientas de build.

## Cambios realizados

- **Eliminación de Vue.js y dependencias:**
  - Se eliminaron todos los archivos de componentes, controladores y configuración de Vue.js (`src/components`, `src/controllers`, `src/main.js`, `src/App.vue`, `src/router.js`).
  - Se eliminaron las dependencias de `vue`, `vue-router`, `@vitejs/plugin-vue` y `vite` del `package.json`.
  - Se eliminó la carpeta `node_modules` y el archivo `package-lock.json` para limpiar cualquier rastro de dependencias.

- **Migración a HTML + Bootstrap:**
  - Se reemplazó el archivo `index.html` por una versión simple que utiliza solo Bootstrap desde CDN.
  - Toda la lógica de vistas y navegación ahora es estática, usando tabs de Bootstrap.
  - No se requiere ningún comando de build ni servidor de desarrollo: solo abre `index.html` en tu navegador.

## Cómo usar

1. Abre el archivo `index.html` directamente en tu navegador.
2. No es necesario instalar dependencias ni ejecutar comandos npm.
3. La interfaz es completamente funcional y visualmente limpia usando solo Bootstrap.

## Ejemplo de código principal

```html
<!-- index.html (fragmento) -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<body class="bg-light">
  <div class="container py-5">
    <nav class="mb-4">
      <ul class="nav nav-pills justify-content-center gap-2">
        <li class="nav-item"><a href="#tareas" class="nav-link active" data-bs-toggle="tab">Tareas</a></li>
        <li class="nav-item"><a href="#usuarios" class="nav-link" data-bs-toggle="tab">Usuarios</a></li>
        <li class="nav-item"><a href="#dashboard" class="nav-link" data-bs-toggle="tab">Dashboard</a></li>
        <li class="nav-item"><a href="#configuracion" class="nav-link" data-bs-toggle="tab">Configuración</a></li>
      </ul>
    </nav>
    <!-- ...contenido de tabs... -->
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
```

## Captura de pantalla sugerida

Puedes agregar aquí una imagen de la interfaz:

![Ejemplo de interfaz Bootstrap](screenshot_frontend_bootstrap.png)

## Ventajas
- Cero dependencias externas.
- Carga ultra rápida.
- Mantenimiento y despliegue extremadamente simples.

---

**Última actualización:** 27 de diciembre de 2025
