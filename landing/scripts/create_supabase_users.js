// Script para crear usuarios de prueba en Supabase
// Requiere: node, @supabase/supabase-js y variables de entorno en .env.local

import { createClient } from '@supabase/supabase-js';
import 'dotenv/config';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

const users = [
  { email: 'superadmin@pulseb2b.com', password: 'SuperSecret123!', role: 'superuser' },
  { email: 'freeuser@pulseb2b.com', password: 'FreeUser123!', role: 'free' },
  { email: 'prouser@pulseb2b.com', password: 'ProUser123!', role: 'pro' },
];

async function main() {
  for (const user of users) {
    const { data, error } = await supabase.auth.admin.createUser({
      email: user.email,
      password: user.password,
      email_confirm: true,
      user_metadata: { role: user.role },
    });
    if (error) {
      console.error(`Error creando ${user.email}:`, error.message);
    } else {
      console.log(`Usuario creado: ${user.email} (${user.role})`);
    }
  }
}

main();
