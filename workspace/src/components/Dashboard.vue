<template>
  <div class="container py-5">
    <h1 class="mb-4 text-center">Dashboard</h1>
    <div class="row">
      <div class="col-md-6 mb-3">
        <div class="card text-bg-primary">
          <div class="card-body">
            <h5 class="card-title">Tareas</h5>
            <p class="card-text">Acceso rápido a la gestión de tareas.</p>
            <router-link to="/" class="btn btn-light">Ir a Tareas</router-link>
          </div>
        </div>
      </div>
      <div class="col-md-6 mb-3">
        <div class="card text-bg-success">
          <div class="card-body">
            <h5 class="card-title">Usuarios</h5>
            <p class="card-text">Ver y administrar usuarios.</p>
            <router-link to="/usuarios" class="btn btn-light">Ir a Usuarios</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
</script>
