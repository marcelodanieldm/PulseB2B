# Automated Lifecycle & Drip Email System

## Infraestructura
- Proveedor: Resend (Node.js SDK)
- Plantillas: React Email o HTML/CSS inline, estética Slate/Indigo
- Tracking: Todos los links con UTM para analytics

## Workflows

### A. Transaccional (Onboarding Enterprise)
- Trigger: Stripe Webhook (checkout.session.completed, price_id Enterprise)
- Acción: Actualiza plan_type en Supabase, envía email onboarding con link a /docs/api

### B. Drip Marketing
- Trigger: Registro de usuario
- Lógica: Secuencia de emails (día 1, 3, 7, 10, 14) si sigue en Free
- Gestión: Cola con Upstash o función programada en Supabase

## Seguridad y Monitoreo
- Unsubscribe: Link funcional en cada email (actualiza marketing_opt_in)
- Secrets: API Keys en Supabase Vault o Vercel Env Vars
- Monitoreo: Tabla email_logs para dashboard

## Archivos Clave
- api/emails/sendTransactional.js: Envío onboarding
- api/emails/sendDrip.js: Envío drip
- supabase/functions/dripScheduler.ts: Scheduler de drip
- supabase/functions/unsubscribe.ts: Unsubscribe handler
- supabase/migrations/2025-12-28_create_email_logs.sql: Tabla de logs
- emails/EnterpriseOnboardingEmail.jsx: Plantilla React Email

---

**Nota:** Personaliza los textos y lógica de la secuencia según tu copy y necesidades de negocio.
