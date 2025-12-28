export default function Audience() {
  return (
    <section className="py-16 px-4 max-w-3xl mx-auto text-center">
      <div className="mb-6">
        <span className="inline-block px-4 py-1 border border-indigo-500/50 rounded-full text-indigo-400 text-xs tracking-wide uppercase">Designed for Software Agencies, HR Leaders, and B2B SaaS Founders.</span>
      </div>
      <div className="flex justify-center gap-4 text-zinc-400 text-lg font-medium">
        <span>USA</span>
        <span className="opacity-60">↔</span>
        <span>ARG</span>
        <span className="opacity-60">↔</span>
        <span>MEX</span>
        <span className="opacity-60">↔</span>
        <span>COL</span>
        <span className="opacity-60">↔</span>
        <span>CAN</span>
      </div>
    </section>
  );
}
