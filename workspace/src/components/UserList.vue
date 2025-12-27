<template>
  <div class="container py-4">
    <h2 class="mb-4">Usuarios</h2>
    <router-view />
    <div v-if="loading" class="text-center my-4">
      <div class="spinner-border text-primary" role="status"></div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th>ID</th>
          <th>Nombre</th>
          <th>Email</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.name }}</td>
          <td>{{ user.email }}</td>
          <td>
            <router-link :to="`/usuarios/${user.id}`" class="btn btn-sm btn-info">Ver detalle</router-link>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import useUserController from '../controllers/UserController.js';

const { users, loading, error, fetchUsers } = useUserController();
onMounted(fetchUsers);
</script>
