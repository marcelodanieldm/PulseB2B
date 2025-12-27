<template>
  <div class="container py-5">
    <h1 class="mb-4 text-center">Configuración</h1>
    <form class="mb-4">
      <div class="mb-3">
        <label for="email" class="form-label">Email de notificaciones</label>
        <input type="email" class="form-control" id="email" placeholder="usuario@ejemplo.com" />
      </div>
      <div class="mb-3">
        <label for="theme" class="form-label">Tema</label>
        <select class="form-select" id="theme">
          <option>Claro</option>
          <option>Oscuro</option>
        </select>
      </div>
      <button class="btn btn-primary" type="submit">Guardar</button>
    </form>
    <div class="alert alert-info">Esta pantalla es solo un ejemplo de configuración.</div>
  </div>
</template>
<script setup>
</script>
