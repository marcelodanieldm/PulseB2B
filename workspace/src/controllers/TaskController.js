// src/controllers/TaskController.js
import { ref } from 'vue';

export default function useTaskController() {
  const tasks = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const fetchTasks = async () => {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetch('https://jsonplaceholder.typicode.com/todos?_limit=5');
      if (!res.ok) throw new Error('Error al cargar tareas');
      tasks.value = await res.json();
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  const addTask = (title) => {
    if (!title.trim()) return;
    tasks.value.unshift({ id: Date.now(), title, completed: false });
  };

  const toggleTask = (id) => {
    tasks.value = tasks.value.map(t => t.id === id ? { ...t, completed: !t.completed } : t);
  };

  const deleteTask = (id) => {
    tasks.value = tasks.value.filter(t => t.id !== id);
  };

  return { tasks, loading, error, fetchTasks, addTask, toggleTask, deleteTask };
}
