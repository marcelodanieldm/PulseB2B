<template>
  <div class="container py-5">
    <nav class="mb-4">
      <ul class="nav nav-pills justify-content-center gap-2">
        <li class="nav-item">
          <router-link to="/" class="nav-link" active-class="active" exact> Tareas </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/usuarios" class="nav-link" active-class="active"> Usuarios </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/dashboard" class="nav-link" active-class="active"> Dashboard </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/configuracion" class="nav-link" active-class="active"> Configuración </router-link>
        </li>
      </ul>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
</script>

<style scoped>
body {
  background: #f8f9fa;
}
</style>
