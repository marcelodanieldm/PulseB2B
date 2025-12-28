import { useState } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

export default function Signup() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    const { error } = await supabase.auth.signUp({ email, password });
    if (error) setMessage(error.message);
    else setMessage('Check your email to confirm your account.');
    setLoading(false);
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-zinc-950">
      <form onSubmit={handleSignup} className="bg-zinc-900/80 p-8 rounded-xl border border-zinc-800 w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-white">Sign Up</h2>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          className="w-full mb-4 px-4 py-2 rounded border border-zinc-700 bg-zinc-950 text-white"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          className="w-full mb-4 px-4 py-2 rounded border border-zinc-700 bg-zinc-950 text-white"
          required
        />
        <button
          type="submit"
          className="w-full py-2 bg-indigo-500 text-white rounded font-semibold hover:bg-indigo-600 transition"
          disabled={loading}
        >
          {loading ? 'Signing up...' : 'Sign Up'}
        </button>
        {message && <div className="mt-4 text-indigo-400 text-sm">{message}</div>}
      </form>
    </div>
  );
}
