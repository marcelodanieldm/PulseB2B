import { useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

export default function Login() {
  useEffect(() => {
    supabase.auth.signInWithOAuth({ provider: 'google' });
  }, []);

  return (
    <div className="flex items-center justify-center min-h-screen bg-zinc-950">
      <div className="text-white text-lg">Redirecting to login...</div>
    </div>
  );
}
