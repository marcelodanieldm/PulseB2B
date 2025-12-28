
import { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

export default function Home() {
  const [role, setRole] = useState(null);

  useEffect(() => {
    const getUserRole = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (user && user.user_metadata && user.user_metadata.role) {
        setRole(user.user_metadata.role);
      }
    };
    getUserRole();
  }, []);

  return (
    <>
      <Head>
        <title>PulseB2B – Predictive Intelligence for Tech Growth</title>
        <meta name="description" content="Stop cold-calling the wrong people. We track funding signals and tech shifts to tell you who is hiring in LATAM before they even post a job." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <div className="bg-zinc-950 min-h-screen font-geist text-white">
        <Navbar />
        {role && (
          <div className="fixed top-4 right-4 bg-indigo-500/90 text-white px-4 py-2 rounded-full text-xs font-semibold z-50 shadow-lg">
            Rol: {role}
          </div>
        )}
        <main>
          <Hero />
          <Features />
          <Comparison />
          <Services />
          <Audience />
        </main>
      </div>
    </>
  );
}
