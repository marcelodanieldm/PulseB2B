<template>
  <div class="container py-5">
    <h1 class="mb-4 text-center">Gestión de Tareas</h1>
    <div v-if="alert" :class="`alert alert-${alert.type} alert-dismissible fade show`" role="alert">
      {{ alert.msg }}
    </div>
    <form class="mb-4" @submit.prevent="onAddTask">
      <div class="input-group">
        <input v-model="newTask" type="text" class="form-control" placeholder="Nueva tarea" />
        <button class="btn btn-success" type="submit">Agregar</button>
      </div>
    </form>
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <table v-else class="table table-striped table-hover">
      <thead>
        <tr>
          <th>#</th>
          <th>Tarea</th>
          <th>Completada</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(task, idx) in tasks" :key="task.id" :class="task.completed ? 'table-success' : ''">
          <td>{{ idx + 1 }}</td>
          <td>{{ task.title }}</td>
          <td>
            <input type="checkbox" v-model="task.completed" @change="onToggleTask(task.id)" />
          </td>
          <td>
            <button class="btn btn-sm btn-danger" @click="onDeleteTask(task.id)">Eliminar</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import useTaskController from '../controllers/TaskController.js';

const { tasks, loading, error, fetchTasks, addTask, toggleTask, deleteTask } = useTaskController();
const newTask = ref('');
const alert = ref(null);

onMounted(fetchTasks);

function onAddTask() {
  addTask(newTask.value);
  alert.value = { type: 'success', msg: 'Tarea agregada' };
  newTask.value = '';
  setTimeout(() => (alert.value = null), 2000);
}
function onToggleTask(id) {
  toggleTask(id);
}
function onDeleteTask(id) {
  deleteTask(id);
  alert.value = { type: 'danger', msg: 'Tarea eliminada' };
  setTimeout(() => (alert.value = null), 2000);
}
</script>
