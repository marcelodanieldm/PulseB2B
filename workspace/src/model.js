
// Modelo: gestiona el estado de tareas y usuarios vía API Flask
const API_URL = 'http://127.0.0.1:5000/api';
const Model = (() => {
  let tasks = [];
  let users = [];

  async function fetchTasks() {
    const res = await fetch(`${API_URL}/tasks`);
    tasks = await res.json();
    return tasks;
  }

  async function addTask(title) {
    const res = await fetch(`${API_URL}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title })
    });
    const task = await res.json();
    tasks.unshift(task);
    return task;
  }

  async function toggleTask(id) {
    const res = await fetch(`${API_URL}/tasks/${id}/toggle`, { method: 'POST' });
    const task = await res.json();
    tasks = tasks.map(t => t.id === id ? task : t);
    return task;
  }

  async function deleteTask(id) {
    await fetch(`${API_URL}/tasks/${id}`, { method: 'DELETE' });
    tasks = tasks.filter(t => t.id !== id);
  }

  async function fetchUsers() {
    const res = await fetch(`${API_URL}/users`);
    users = await res.json();
    return users;
  }

  async function addUser(name, email) {
    const res = await fetch(`${API_URL}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email })
    });
    const user = await res.json();
    users.unshift(user);
    return user;
  }

  return {
    fetchTasks,
    addTask,
    toggleTask,
    deleteTask,
    fetchUsers,
    addUser,
    getTasks: () => tasks,
    getUsers: () => users
  };
})();

export default Model;
