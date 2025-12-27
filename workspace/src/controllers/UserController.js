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
