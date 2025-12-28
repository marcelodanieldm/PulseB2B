
import { motion } from 'framer-motion';
import StripeButton from './StripeButton';

export default function Hero() {
  return (
    <section className="flex flex-col items-center justify-center text-center py-24 px-4 relative overflow-hidden">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8 }}
        className="relative z-10"
      >
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-4 relative">
          <span className="relative inline-block">
            Predictive Intelligence for Tech Growth.
            <span className="absolute -inset-2 -z-10 bg-gradient-to-r from-indigo-500/20 to-transparent rounded-xl blur-2xl animate-pulse" />
          </span>
        </h1>
        <p className="max-w-xl mx-auto text-lg md:text-2xl text-zinc-300 mb-8">
          Stop cold-calling the wrong people. We track funding signals and tech shifts to tell you who is hiring in LATAM before they even post a job.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <StripeButton priceId="price_xxxxxxxxxxxxx" />
          <a href="https://t.me/+jointelegram" target="_blank" rel="noopener" className="px-8 py-3 border border-indigo-500 text-indigo-500 rounded-full font-semibold hover:bg-indigo-500/10 transition">Join Telegram</a>
        </div>
      </motion.div>
      <div className="absolute inset-0 pointer-events-none z-0">
        <div className="w-full h-full bg-gradient-to-br from-indigo-500/5 via-zinc-950 to-zinc-950 blur-2xl" />
      </div>
    </section>
  );
}
