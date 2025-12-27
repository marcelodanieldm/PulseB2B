# Ejemplo de Nuevas Vistas y Controladores en PulseB2B (Vue.js)

## Ejemplo: Vista de Usuarios y Controlador

### 1. Controlador de Usuarios (src/controllers/UserController.js)
```js
import { ref } from 'vue';

export default function useUserController() {
  const users = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const fetchUsers = async () => {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetch('https://jsonplaceholder.typicode.com/users');
      if (!res.ok) throw new Error('Error al cargar usuarios');
      users.value = await res.json();
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  return { users, loading, error, fetchUsers };
}
```

### 2. Vista de Usuarios (src/components/UserList.vue)
```vue
<template>
  <div class="container py-4">
    <h2 class="mb-3">Usuarios</h2>
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
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.name }}</td>
          <td>{{ user.email }}</td>
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
```

---

# Guía de Pantallas y Flujos de Negocio

## 1. Pantalla de Tareas
- **Ruta:** `/`
- **Funcionalidad:** Listar, agregar, eliminar y marcar tareas como completadas.
- **Controlador:** `TaskController.js`
- **Vista:** `App.vue`

## 2. Pantalla de Usuarios
- **Ruta:** `/usuarios`
- **Funcionalidad:** Listar usuarios del sistema.
- **Controlador:** `UserController.js`
- **Vista:** `UserList.vue`

## 3. Pantalla de Dashboard (ejemplo)
- **Ruta:** `/dashboard`
- **Funcionalidad:** Resumen de métricas clave, acceso rápido a tareas y usuarios.
- **Controlador:** (puede combinar datos de varios controladores)
- **Vista:** `Dashboard.vue`

## 4. Pantalla de Configuración (ejemplo)
- **Ruta:** `/configuracion`
- **Funcionalidad:** Preferencias del usuario, integración con APIs, etc.
- **Controlador:** `SettingsController.js`
- **Vista:** `Settings.vue`

---

# Cómo Agregar Nuevas Vistas y Controladores
1. Crea el controlador en `src/controllers/` siguiendo el patrón de los ejemplos.
2. Crea la vista en `src/components/` usando `<script setup>` y Bootstrap.
3. Importa y usa la vista en `App.vue` o en el router si usas Vue Router.
4. Mantén la lógica de negocio en los controladores y la UI en las vistas.

¿Quieres que agregue alguna de estas vistas y controladores al proyecto?