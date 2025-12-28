# Superuser Dashboard: Notificaciones en Tiempo Real

## Funcionalidad
- Muestra notificaciones de nuevos usuarios Pro y usuarios que se desuscribieron.
- Detalle: nombre, email, hora, día, país (por IP), IP.
- Refresca automáticamente cada 30 segundos.
- Endpoint backend: `/api/admin/notifications` (Flask, memoria, listo para DB real).
- Frontend: `SuperuserNotifications.vue` (ruta `/admin/notificaciones`).

## Backend
- `backend/views/notifications_api.py`: Blueprint con endpoint GET `/api/admin/notifications`.
- Función `add_notification(type, name, email, ip, country)` para registrar eventos desde Stripe webhook y desuscripción.
- Respuesta: lista de notificaciones recientes, filtrables por tipo.

## Frontend
- `src/components/SuperuserNotifications.vue`:
  - Consume el endpoint backend.
  - Muestra listas separadas para nuevos Pro y desuscripciones.
  - Refresca cada 30s.

## Extensión
- Listo para conectar a WebSockets para notificaciones push.
- Listo para migrar a base de datos real.

---

**Nota:** Para producción, conecta `add_notification` a los flujos de upgrade y desuscripción reales, y almacena en DB.
