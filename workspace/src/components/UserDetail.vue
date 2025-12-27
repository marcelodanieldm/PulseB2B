<template>
  <div class="container py-4">
    <div v-if="loading" class="text-center my-4">
      <div class="spinner-border text-primary" role="status"></div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else-if="user">
      <h3>Detalle de Usuario</h3>
      <ul class="list-group mb-3">
        <li class="list-group-item"><b>ID:</b> {{ user.id }}</li>
        <li class="list-group-item"><b>Nombre:</b> {{ user.name }}</li>
        <li class="list-group-item"><b>Email:</b> {{ user.email }}</li>
        <li class="list-group-item"><b>Teléfono:</b> {{ user.phone }}</li>
        <li class="list-group-item"><b>Website:</b> {{ user.website }}</li>
      </ul>
      <router-link to="/usuarios" class="btn btn-secondary">Volver a la lista</router-link>
    </div>
    <div v-else class="alert alert-warning">Usuario no encontrado.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const user = ref(null);
const loading = ref(false);
const error = ref(null);
const route = useRoute();

onMounted(async () => {
  loading.value = true;
  try {
    const res = await fetch(`https://jsonplaceholder.typicode.com/users/${route.params.id}`);
    if (!res.ok) throw new Error('Error al cargar usuario');
    user.value = await res.json();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
});
</script>
