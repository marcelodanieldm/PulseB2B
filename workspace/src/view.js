// Vista: renderiza tareas y usuarios en el DOM

const View = (() => {
  function setTaskLoading(loading) {
    document.getElementById('task-loading').style.display = loading ? '' : 'none';
  }
  function setTaskError(msg) {
    const el = document.getElementById('task-error');
    el.textContent = msg || '';
    el.style.display = msg ? '' : 'none';
  }
  function renderTasks(tasks) {
    const tbody = document.getElementById('task-tbody');
    tbody.innerHTML = '';
    tasks.forEach((task, idx) => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${idx + 1}</td>
        <td>${task.title}</td>
        <td><input type="checkbox" ${task.completed ? 'checked' : ''} data-id="${task.id}" class="toggle-task"></td>
        <td><button class="bg-red-600 text-white px-2 py-1 rounded delete-task" data-id="${task.id}">Eliminar</button></td>
      `;
      tbody.appendChild(row);
    });
  }

  function setUserLoading(loading) {
    document.getElementById('user-loading').style.display = loading ? '' : 'none';
  }
  function setUserError(msg) {
    const el = document.getElementById('user-error');
    el.textContent = msg || '';
    el.style.display = msg ? '' : 'none';
  }
  function renderUsers(users) {
    const tbody = document.getElementById('user-tbody');
    tbody.innerHTML = '';
    users.forEach((user, idx) => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${user.id}</td>
        <td>${user.name}</td>
        <td>${user.email}</td>
        <td></td>
      `;
      tbody.appendChild(row);
    });
  }

  return { renderTasks, renderUsers, setTaskLoading, setTaskError, setUserLoading, setUserError };
})();

export default View;
