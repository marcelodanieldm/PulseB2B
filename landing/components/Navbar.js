import Link from 'next/link';

export default function Navbar() {
  return (
    <header className="flex justify-between items-center px-6 py-4 border-b border-zinc-800/60">
      <div className="text-xl font-bold tracking-tight">PulseB2B</div>
      <nav className="flex gap-6 items-center text-sm">
        <Link href="#features" className="hover:text-indigo-500 transition">Features</Link>
        <Link href="#pricing" className="hover:text-indigo-500 transition">Pricing</Link>
        <Link href="#docs" className="hover:text-indigo-500 transition">Docs</Link>
        <Link href="/login" className="ml-4 px-4 py-1 border border-indigo-500 text-indigo-500 rounded-full font-medium hover:bg-indigo-500/10 transition-all" prefetch={false}>Login</Link>
      </nav>
    </header>
  );
}
