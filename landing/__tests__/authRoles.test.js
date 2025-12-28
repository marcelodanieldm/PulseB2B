const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

describe('Supabase Auth Roles', () => {
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  );

  const users = [
    { email: 'superadmin@pulseb2b.com', password: 'SuperSecret123!', expectedRole: 'superuser' },
    { email: 'freeuser@pulseb2b.com', password: 'FreeUser123!', expectedRole: 'free' },
    { email: 'prouser@pulseb2b.com', password: 'ProUser123!', expectedRole: 'pro' },
  ];

  users.forEach(({ email, password, expectedRole }) => {
    test(`El usuario ${email} debe tener el rol ${expectedRole}`, async () => {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      expect(error).toBeNull();
      expect(data.user).toBeDefined();
      expect(data.user.user_metadata.role).toBe(expectedRole);
    });
  });
});
