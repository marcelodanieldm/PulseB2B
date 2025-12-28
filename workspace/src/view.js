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

  function renderUserPanel(user, tasks, notifications = []) {
    const panel = document.getElementById('user-panel');
    panel.innerHTML = '';
    // Notificaciones
    if (notifications.length > 0) {
      const notifDiv = document.createElement('div');
      notifDiv.className = 'mb-4 p-2 bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700';
      notifDiv.innerHTML = notifications.map(n => `<div>${n}</div>`).join('');
      panel.appendChild(notifDiv);
    }
    // ...rest of user panel rendering (tasks, etc)...
  }

  function showPanelNotification(type, message) {
    // type: 'free' | 'pro'
    const panel = document.getElementById('user-panel');
    let notif = document.createElement('div');
    notif.className = `${type}-panel-notification mb-2 p-2 bg-blue-100 border-l-4 border-blue-500 text-blue-700`;
    notif.textContent = message;
    panel.prepend(notif);
    setTimeout(() => notif.remove(), 8000);
  }

  return { renderTasks, renderUsers, setTaskLoading, setTaskError, setUserLoading, setUserError, renderUserPanel, showPanelNotification };
})();

export default View;
