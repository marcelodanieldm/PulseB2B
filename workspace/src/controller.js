// Renderiza la vista de servicios activos para usuario Pro
export function showProServicesForUser() {
  // Oculta otras secciones
  document.querySelectorAll('section, .tab-content-section').forEach(el => el.classList.add('hidden'));
  // Muestra la sección de servicios Pro
  document.getElementById('pro-services').classList.remove('hidden');
  // Lógica de botones
  setTimeout(() => {
    // Stripe portal (real)
    const portal = document.getElementById('stripe-portal-link-pro');
    if (portal) portal.onclick = async (e) => {
      e.preventDefault();
      try {
        const res = await fetch('/api/billing/create-customer-portal', { method: 'POST', credentials: 'include' });
        if (!res.ok) throw new Error('Error opening portal');
        const data = await res.json();
        window.location.href = data.url;
      } catch (err) {
        alert('Error connecting to Stripe portal.');
      }
    };
    // Contact Sales (Enterprise)
    const contact = document.querySelector('#pro-services .bg-yellow-400');
    if (contact) contact.onclick = () => {
      window.open('mailto:sales@pulseb2b.com?subject=Interested%20in%20Custom%20Alert%20API', '_blank');
    };
    // Unsubscribe (real)
    const unsub = document.querySelector('#pro-services .bg-zinc-800');
    if (unsub) unsub.onclick = async () => {
      if (!confirm('Are you sure you want to cancel your subscription?')) return;
      try {
        const res = await fetch('/api/billing/cancel-subscription', { method: 'POST', credentials: 'include' });
        if (!res.ok) throw new Error('Error cancelling subscription');
        alert('Subscription cancelled. Your access will end at the end of the billing period.');
        window.location.reload();
      } catch (err) {
        alert('Error cancelling subscription.');
      }
    };
  }, 100);
}
// Dispara el Upgrade Modal en elementos bloqueados
export function setupLockedFeatureTriggers() {
  // Elementos con clase .blur-locked o .locked-feature
  document.querySelectorAll('.blur-locked, .locked-feature').forEach(el => {
    el.style.cursor = 'pointer';
    el.onclick = (e) => {
      e.preventDefault();
      if (typeof window.showUpgradeModal === 'function') window.showUpgradeModal();
    };
  });
}
// Hook global para mostrar el Upgrade Modal premium
export function useUpgradeModal() {
  window.showUpgradeModal = function() {
    document.getElementById('upgrade-modal').classList.remove('hidden');
  };
  document.getElementById('close-upgrade-modal').onclick = () => {
    document.getElementById('upgrade-modal').classList.add('hidden');
  };
  document.getElementById('upgrade-modal-cta').onclick = async () => {
    // Llama al backend para crear sesión de Stripe Checkout
    try {
      const res = await fetch('/api/billing/create-checkout-session', { method: 'POST', credentials: 'include' });
      if (!res.ok) throw new Error('Error creating checkout session');
      const data = await res.json();
      window.location.href = data.url;
    } catch (err) {
      alert('Error connecting to payment gateway.');
    }
  };
}

// Confetti effect tras pago exitoso (simulación)
export function showConfetti() {
  // Simple confetti effect (puedes reemplazar por una librería real)
  const confetti = document.createElement('div');
  confetti.style.position = 'fixed';
  confetti.style.inset = 0;
  confetti.style.pointerEvents = 'none';
  confetti.style.zIndex = 9999;
  confetti.innerHTML = '<div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);font-size:4rem;">🎉</div>';
  document.body.appendChild(confetti);
  setTimeout(() => confetti.remove(), 2000);
}
// Lógica de botones y modales para Premium Upsell
export function setupPremiumUpsellLogic() {
  // Toggle mensual/anual
  const toggle = document.getElementById('toggle-billing-cycle');
  const badge = document.getElementById('yearly-badge');
  const proPrice = document.querySelector('#upgrade-pro-btn').parentElement.querySelector('div.absolute');
  let yearly = false;
  toggle.addEventListener('click', () => {
    yearly = !yearly;
    badge.classList.toggle('hidden', !yearly);
    proPrice.textContent = yearly ? '$290/año' : '$29/mo';
  });

  // Upgrade to Pro (Stripe Checkout)
  document.getElementById('upgrade-pro-btn').onclick = () => {
    // Simulación: redirige a Stripe Checkout (reemplaza con tu link real)
    window.location.href = 'https://buy.stripe.com/test_1234567890';
  };

  // Contact Sales (Enterprise)
  document.getElementById('contact-sales-btn').onclick = () => {
    window.open('mailto:sales@pulseb2b.com?subject=Interesado%20en%20Custom%20Alert%20API', '_blank');
  };

  // Stripe Customer Portal
  document.getElementById('stripe-portal-link').onclick = (e) => {
    e.preventDefault();
    window.location.href = 'https://billing.stripe.com/p/session/test_portal_123';
  };

  // Modal Feature Gate (Upsell)
  document.querySelectorAll('.feature-gate-btn').forEach(btn => {
    btn.onclick = () => {
      document.getElementById('feature-gate-modal').classList.remove('hidden');
    };
  });
  document.getElementById('close-feature-gate').onclick = () => {
    document.getElementById('feature-gate-modal').classList.add('hidden');
  };
  document.getElementById('modal-upgrade-pro-btn').onclick = () => {
    window.location.href = 'https://buy.stripe.com/test_1234567890';
  };

  // Modal Payment Success (simulación)
  window.showPaymentSuccess = function() {
    document.getElementById('payment-success-modal').classList.remove('hidden');
  };
  document.getElementById('close-payment-success').onclick = () => {
    document.getElementById('payment-success-modal').classList.add('hidden');
    // Simula recarga de dashboard Pro
    window.location.reload();
  };
}
// Renderiza la vista de planes y servicios para usuario Free
export function showBillingPlansForFreeUser() {
  // Oculta otras secciones
  document.querySelectorAll('section, .tab-content-section').forEach(el => el.classList.add('hidden'));
  // Muestra la sección de planes
  document.getElementById('billing-plans').classList.remove('hidden');
  // Muestra la sección de upsell premium
  document.getElementById('premium-upsell').classList.remove('hidden');
  // Inicializa lógica de botones, modales y triggers de features bloqueadas
  setTimeout(() => {
    if (typeof window !== 'undefined') {
      import('./controller.js').then(mod => {
        mod.setupPremiumUpsellLogic();
        mod.useUpgradeModal();
        mod.setupLockedFeatureTriggers();
      });
    }
  }, 100);
}
// Controlador: conecta modelo y vista, maneja eventos
import Model from './model.js';
import View from './view.js';
import { sendNotification, fetchNotifications } from './model.js';
import { showPanelNotification } from './view.js';
import { showUserPanelWithNotifications } from './controller.js';


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

let currentUser = null;

async function login(username, password) {
  const res = await fetch('http://127.0.0.1:5000/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ username, password })
  });
  if (res.ok) {
    const data = await res.json();
    currentUser = data;
    // Si el usuario es Free, mostrar la vista de planes y servicios
    if (data.role === 'free') {
      import('./controller.js').then(mod => mod.showBillingPlansForFreeUser());
    } else if (data.role === 'pro') {
      import('./controller.js').then(mod => mod.showProServicesForUser());
    }
    return data;
  } else {
    const err = await res.json();
    throw new Error(err.error || 'Error de autenticación');
  }
}

async function logout() {
  await fetch('http://127.0.0.1:5000/api/logout', {
    method: 'POST',
    credentials: 'include'
  });
  currentUser = null;
}

async function getCurrentUser() {
  const res = await fetch('http://127.0.0.1:5000/api/me', { credentials: 'include' });
  if (res.ok) {
    currentUser = await res.json();
    return currentUser;
  }
  currentUser = null;
  return null;
}

let adminUsersCache = [];

async function fetchAdminUsers() {
  // Simulación: usa Model.fetchUsers() y agrega roles ficticios
  const users = await Model.fetchUsers();
  // Demo: asigna rol 'pro' a los pares, 'free' a los impares
  return users.map((u, i) => ({ ...u, role: i % 2 === 0 ? 'pro' : 'free', country: 'AR', service: i % 2 === 0 ? 'Premium' : 'Free' }));
}

function renderAdminUsers(users) {
  const tbody = document.getElementById('admin-user-tbody');
  tbody.innerHTML = '';
  users.forEach((user) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${user.id}</td>
      <td><input type="text" value="${user.name}" class="admin-edit-name" data-id="${user.id}" /></td>
      <td><input type="text" value="${user.email}" class="admin-edit-email" data-id="${user.id}" /></td>
      <td>${user.role}</td>
      <td>
        <button class="bg-green-600 text-white px-2 py-1 rounded admin-save-user" data-id="${user.id}">Guardar</button>
        <button class="bg-red-600 text-white px-2 py-1 rounded admin-delete-user" data-id="${user.id}">Eliminar</button>
      </td>
    `;
    tbody.appendChild(row);
  });
}

function filterAdminUsers(type) {
  if (type === 'all') return adminUsersCache;
  return adminUsersCache.filter(u => u.role === type);
}

function setupAdminUserFilter() {
  const filter = document.getElementById('user-type-filter');
  filter.addEventListener('change', () => {
    renderAdminUsers(filterAdminUsers(filter.value));
  });
}

function setupAdminUserEvents(users) {
  const tbody = document.getElementById('admin-user-tbody');
  tbody.addEventListener('click', async (e) => {
    if (e.target.classList.contains('admin-save-user')) {
      const id = Number(e.target.dataset.id);
      const name = tbody.querySelector(`.admin-edit-name[data-id='${id}']`).value;
      const email = tbody.querySelector(`.admin-edit-email[data-id='${id}']`).value;
      users.find(u => u.id === id).name = name;
      users.find(u => u.id === id).email = email;
      document.getElementById('admin-user-msg').textContent = 'Usuario actualizado (demo)';
      setTimeout(() => document.getElementById('admin-user-msg').textContent = '', 2000);
    }
    if (e.target.classList.contains('admin-delete-user')) {
      const id = Number(e.target.dataset.id);
      const idx = users.findIndex(u => u.id === id);
      if (idx !== -1) users.splice(idx, 1);
      adminUsersCache = users;
      renderAdminUsers(filterAdminUsers(document.getElementById('user-type-filter').value));
      document.getElementById('admin-user-msg').textContent = 'Usuario eliminado (demo)';
      setTimeout(() => document.getElementById('admin-user-msg').textContent = '', 2000);
    }
  });
}

function setupAdminMessageForm() {
  const form = document.getElementById('admin-message-form');
  const status = document.getElementById('admin-message-status');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const type = document.getElementById('message-type').value;
    const msg = document.getElementById('admin-message').value.trim();
    if (!msg) {
      status.textContent = 'El mensaje no puede estar vacío.';
      return;
    }
    try {
      await sendNotification(msg, type);
      status.textContent = `Mensaje enviado a ${type === 'all' ? 'todos los usuarios' : 'usuarios ' + type}`;
      form.reset();
    } catch (err) {
      status.textContent = 'Error enviando notificación';
    }
    setTimeout(() => status.textContent = '', 2000);
  });
}

export async function showUserPanelWithNotifications(user) {
  // user.role: 'free' | 'pro' | ...
  const notifs = await fetchNotifications(user.role);
  // Render panel with notifications (view.js)
  import('./view.js').then(view => {
    view.renderUserPanel(user, [], notifs.map(n => n.message));
  });
}

async function showSuperadminPanel() {
  const users = await fetchAdminUsers();
  adminUsersCache = users;
  renderAdminUsers(users);
  setupAdminUserEvents(users);
  setupAdminUserFilter();
  setupAdminMessageForm();
  renderAdminReports(users);
  renderAdminKPIs(users);
}

function renderAdminReports(users) {
  // Reportes demo
  const free = users.filter(u => u.role === 'free').length;
  const pro = users.filter(u => u.role === 'pro').length;
  document.getElementById('report-free-users').textContent = free;
  document.getElementById('report-pro-users').textContent = pro;
  document.getElementById('report-ip-country').textContent = 'Argentina (demo)';
  document.getElementById('report-service').textContent = pro > 0 ? 'Premium' : 'Free';
}

function renderAdminKPIs(users) {
  // KPIs demo
  document.getElementById('kpi-active-users').textContent = users.length;
  document.getElementById('kpi-completed-tasks').textContent = '12 (demo)';
  document.getElementById('kpi-sales').textContent = '5 (demo)';
  document.getElementById('kpi-revenue').textContent = '$5000 (demo)';
}

function showSectionByRole(role) {
  // Ejemplo: solo superadmin ve dashboard y panel superadmin, clientepro ve tareas/usuarios y panel pro
  document.getElementById('dashboard').style.display = (role === 'superadmin') ? '' : 'none';
  document.getElementById('superadmin-panel').classList.toggle('hidden', role !== 'superadmin');
  document.getElementById('pro-panel').classList.toggle('hidden', role !== 'clientepro');
  document.getElementById('tareas').style.display = (role === 'clientepro') ? '' : 'none';
  document.getElementById('usuarios').style.display = (role === 'clientepro') ? '' : 'none';
  if (role === 'superadmin') {
    showSuperadminPanel();
  }
}

function setupAuthUI() {
  const loginForm = document.getElementById('login-form');
  const loginPage = document.getElementById('login-page');
  const logoutBtn = document.getElementById('logout-btn');
  const loginError = document.getElementById('login-error');

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    try {
      const user = await login(username, password);
      loginPage.classList.add('hidden');
      showSectionByRole(user.role);
      loginError.classList.add('hidden');
      // Set window.currentUser and localStorage for Pro demo
      window.currentUser = user;
      localStorage.setItem('user-role', user.role);
    } catch (err) {
      loginError.textContent = err.message;
      loginError.classList.remove('hidden');
    }
  });

  logoutBtn.addEventListener('click', async () => {
    await logout();
    document.getElementById('login-page').classList.remove('hidden');
    document.getElementById('tareas').style.display = 'none';
    document.getElementById('usuarios').style.display = 'none';
    document.getElementById('dashboard').style.display = 'none';
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
  await getCurrentUser();
  if (!currentUser) {
    document.getElementById('login-page').classList.remove('hidden');
    document.getElementById('tareas').style.display = 'none';
    document.getElementById('usuarios').style.display = 'none';
    document.getElementById('dashboard').style.display = 'none';
  } else {
    showSectionByRole(currentUser.role);
  }
  setupAuthUI();
  setupTaskEvents();
  setupUserEvents();
}

document.addEventListener('DOMContentLoaded', init);

async function showUserPanel(user) {
  await showUserPanelWithNotifications(user);
  // ...cargar tareas, etc, si aplica...
}
