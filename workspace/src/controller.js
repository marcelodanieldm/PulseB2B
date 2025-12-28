// Controlador: conecta modelo y vista, maneja eventos
import Model from './model.js';
import View from './view.js';


function setupTaskEvents() {
  document.getElementById('task-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('task-input');
    const title = input.value.trim();
    if (!title) return;
    await Model.addTask(title);
    View.renderTasks(Model.getTasks());
    input.value = '';
  });

  document.getElementById('task-tbody').addEventListener('click', async (e) => {
    if (e.target.classList.contains('delete-task')) {
      const id = Number(e.target.dataset.id);
      await Model.deleteTask(id);
      View.renderTasks(Model.getTasks());
    }
    if (e.target.classList.contains('toggle-task')) {
      const id = Number(e.target.dataset.id);
      await Model.toggleTask(id);
      View.renderTasks(Model.getTasks());
    }
  });
}

function setupUserEvents() {
  document.getElementById('user-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('user-name').value.trim();
    const email = document.getElementById('user-email').value.trim();
    if (!name || !email) return;
    await Model.addUser(name, email);
    View.renderUsers(Model.getUsers());
  });
}


async function init() {
  // Tareas
  View.setTaskLoading(true);
  View.setTaskError('');
  try {
    await Model.fetchTasks();
    View.renderTasks(Model.getTasks());
  } catch (e) {
    View.setTaskError('Error al cargar tareas');
  } finally {
    View.setTaskLoading(false);
  }
  // Usuarios
  View.setUserLoading(true);
  View.setUserError('');
  try {
    await Model.fetchUsers();
    View.renderUsers(Model.getUsers());
  } catch (e) {
    View.setUserError('Error al cargar usuarios');
  } finally {
    View.setUserLoading(false);
  }
  setupTaskEvents();
  setupUserEvents();
}

document.addEventListener('DOMContentLoaded', init);
