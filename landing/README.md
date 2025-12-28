## Testing de roles de usuario

Hay tests unitarios en `__tests__/authRoles.test.js` para validar el flujo de sign in y el rol de cada usuario (superuser, free, pro) usando Jest.

### Ejecutar tests

1. Asegúrate de tener las variables reales de Supabase en `.env`.
2. Instala dependencias de test:
	```
	npm install --save-dev jest dotenv
	```
3. Ejecuta:
	```
	npx jest __tests__/authRoles.test.js
	```
4. El test validará que cada usuario accede y tiene el rol correcto.
# PulseB2B Landing Page

This folder contains the new high-conversion, minimalist, and premium landing page for PulseB2B, inspired by the "Stealth Hunter" concept.

## Stack
- Next.js 14
- Tailwind CSS
- Framer Motion

## Design
- Dark mode (zinc-950 background)
- Geist or Inter font, tracking-tight
- Ultra-thin borders
- Indigo-500 accents

## Sections
- Minimalist header
- Hero section with animated headline
- Bento grid features
- Comparison table
- Audience callout
- Interactive services section


## Auth & Payments

- **Supabase Auth**: Email/password y Google OAuth habilitados. Configura las variables en `.env.local`:
	- `NEXT_PUBLIC_SUPABASE_URL`
	- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

- **Stripe**: Suscripción mensual vía Stripe Checkout. Configura en `.env.local`:
	- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`
	- `STRIPE_SECRET_KEY`
	- Reemplaza el `priceId` en `components/Hero.js` por el ID real de tu producto Stripe.

## Flujos

- **Sign Up**: `/signup` (email/password)
- **Sign In**: `/signin` (email/password)
- **Login Google**: `/login` (OAuth)
- **Pago**: Botón "Start for $29/mo" en el Hero (Stripe Checkout)

## Notas

- El backend de Stripe requiere Node.js 18+ para funcionar correctamente.
- Asegúrate de tener las variables de entorno correctas antes de ejecutar el proyecto.
