export default function Features() {
  return (
    <section id="features" className="py-20 px-4 max-w-6xl mx-auto">
      <div className="grid md:grid-cols-3 gap-8">
        <div className="bg-zinc-900/80 border border-zinc-800 rounded-2xl p-8 shadow-sm hover:border-indigo-500/50 transition-all">
          <h3 className="text-xl font-semibold mb-2">Real-time Signal</h3>
          <p className="text-zinc-400 mb-2">24/7 SEC and News monitoring.</p>
        </div>
        <div className="bg-zinc-900/80 border border-zinc-800 rounded-2xl p-8 shadow-sm hover:border-indigo-500/50 transition-all">
          <h3 className="text-xl font-semibold mb-2">Tech-Stack Dossier</h3>
          <p className="text-zinc-400 mb-2">Deep visibility into architecture.</p>
        </div>
        <div className="bg-zinc-900/80 border border-zinc-800 rounded-2xl p-8 shadow-sm hover:border-indigo-500/50 transition-all">
          <h3 className="text-xl font-semibold mb-2">Arbitrage Score</h3>
          <p className="text-zinc-400 mb-2">Financial logic for US-LATAM hiring.</p>
        </div>
      </div>
    </section>
  );
}
