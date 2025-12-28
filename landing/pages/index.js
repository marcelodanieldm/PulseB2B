import Head from 'next/head';
import Hero from '../components/Hero';
import Features from '../components/Features';
import Comparison from '../components/Comparison';
import Services from '../components/Services';
import Audience from '../components/Audience';
import Navbar from '../components/Navbar';

export default function Home() {
  return (
    <>
      <Head>
        <title>PulseB2B – Predictive Intelligence for Tech Growth</title>
        <meta name="description" content="Stop cold-calling the wrong people. We track funding signals and tech shifts to tell you who is hiring in LATAM before they even post a job." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <div className="bg-zinc-950 min-h-screen font-geist text-white">
        <Navbar />
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
