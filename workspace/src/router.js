import { createRouter, createWebHistory } from 'vue-router';
import TaskView from './components/TaskView.vue';
import UserList from './components/UserList.vue';
import UserDetail from './components/UserDetail.vue';
import Dashboard from './components/Dashboard.vue';

import Settings from './components/Settings.vue';
import SuperuserNotifications from './components/SuperuserNotifications.vue';

const routes = [
  { path: '/', name: 'Tareas', component: TaskView },
  {
    path: '/usuarios',
    name: 'Usuarios',
    component: UserList,
    children: [
      {
        path: ':id',
        name: 'UserDetail',
        component: UserDetail,
      },
    ],
  },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard },
  { path: '/configuracion', name: 'Configuración', component: Settings },
  { path: '/admin/notificaciones', name: 'Notificaciones', component: SuperuserNotifications },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
