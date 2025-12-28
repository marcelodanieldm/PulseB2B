export default function Comparison() {
  return (
    <section className="py-20 px-4 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6 text-center">PulseB2B vs. Traditional Databases</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full border-collapse text-sm bg-zinc-900/80 border border-zinc-800 rounded-xl">
          <thead>
            <tr className="text-zinc-400">
              <th className="px-6 py-3 border-b border-zinc-800 font-medium">Feature</th>
              <th className="px-6 py-3 border-b border-zinc-800 font-medium">PulseB2B</th>
              <th className="px-6 py-3 border-b border-zinc-800 font-medium">Traditional DBs</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="px-6 py-4 border-b border-zinc-800">Signal Recency</td>
              <td className="px-6 py-4 border-b border-zinc-800 text-indigo-400 font-semibold">Real-time</td>
              <td className="px-6 py-4 border-b border-zinc-800">Monthly/Quarterly</td>
            </tr>
            <tr>
              <td className="px-6 py-4 border-b border-zinc-800">Cost-Efficiency</td>
              <td className="px-6 py-4 border-b border-zinc-800 text-indigo-400 font-semibold">High</td>
              <td className="px-6 py-4 border-b border-zinc-800">Low</td>
            </tr>
            <tr>
              <td className="px-6 py-4">Data Volume</td>
              <td className="px-6 py-4 text-indigo-400 font-semibold">Curated</td>
              <td className="px-6 py-4">Massive, Unfiltered</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}
