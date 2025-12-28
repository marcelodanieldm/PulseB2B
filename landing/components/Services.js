const services = [
  {
    title: 'Daily Signal',
    value: 'Save 20 hours of prospecting/week',
    result: '10x higher response rate',
    description: 'Get daily alerts on companies showing intent to hire, before jobs are posted.'
  },
  {
    title: 'Weekly Radar',
    value: 'Stay ahead of market shifts',
    result: 'Spot trends before competitors',
    description: 'A weekly digest of funding, tech stack changes, and hiring signals.'
  },
  {
    title: 'Pro Dashboard',
    value: 'Full visibility & analytics',
    result: 'Data-driven sales strategy',
    description: 'Access a dashboard with deep company dossiers and actionable insights.'
  },
  {
    title: 'Custom API',
    value: 'Integrate with your stack',
    result: 'Automate your workflows',
    description: 'Direct API access for custom integrations and advanced use cases.'
  }
];

export default function Services() {
  return (
    <section className="py-20 px-4 max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold mb-10 text-center">Our Service Tiers</h2>
      <div className="grid md:grid-cols-4 gap-6">
        {services.map((s, i) => (
          <div
            key={s.title}
            className="bg-zinc-900/80 border border-zinc-800 rounded-2xl p-6 shadow-sm hover:border-indigo-500/50 transition-all group"
          >
            <h3 className="text-lg font-semibold mb-2 group-hover:text-indigo-400 transition">{s.title}</h3>
            <p className="text-zinc-400 mb-2 text-sm">{s.description}</p>
            <div className="mt-4 text-xs">
              <span className="block text-zinc-500">Value:</span>
              <span className="font-medium text-white">{s.value}</span>
            </div>
            <div className="mt-2 text-xs">
              <span className="block text-zinc-500">Result:</span>
              <span className="font-medium text-indigo-400">{s.result}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
