# Visualización de Usuarios (Superuser Dashboard)

## Funcionalidad
- Muestra conteo de usuarios Free, Pro y Enterprise.
- Lista usuarios por servicio contratado (Webhooks, Slack, HubSpot, API, etc).
- Lista usuarios por país de origen (basado en IP o perfil).
- Ruta: `/admin/usuarios` (componente `UserStats.vue`).

## Backend (pendiente de integración real)
- El componente está listo para consumir un endpoint tipo `/api/admin/user-stats` que devuelva:
  - freeCount, proCount, enterpriseCount
  - usersByService: { servicio: cantidad }
  - usersByCountry: { país: cantidad }
- Actualmente usa datos mock para visualización inmediata.

## Frontend
- `src/components/UserStats.vue`: visualización responsiva, estética Slate/Indigo.
- Se puede refrescar automáticamente o bajo demanda.

---

**Nota:** Para producción, conecta el fetch a tu backend real y asegúrate de actualizar los datos en tiempo real.
