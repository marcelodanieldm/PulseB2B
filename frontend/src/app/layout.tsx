/**
 * Root Layout
 * Global styles and providers with performance optimizations
 */

import './globals.css';

export const metadata = {
  title: 'PulseB2B - Global Venture Intelligence Platform',
  description: 'Real-time market intelligence tracking US, Brazil, and Mexico ventures with high offshore potential. Discover Series A-C startups showing critical hiring signals and scalability indicators.',
  keywords: 'venture intelligence, market signals, offshore potential, Series A startups, Series B funding, Series C ventures, runway analysis, scalability metrics, hiring signals, Latin America tech, US ventures, Brazil startups, Mexico tech companies, B2B intelligence, venture capital, growth signals',
  openGraph: {
    title: 'PulseB2B - Premium Venture Intelligence',
    description: 'Track critical hiring signals from 10,000+ ventures across US, Brazil, and Mexico. Real-time runway analysis and offshore potential scoring.',
    type: 'website',
    url: 'https://pulseb2b.vercel.app',
    siteName: 'PulseB2B',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'PulseB2B Global Signal Map',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'PulseB2B - Global Venture Intelligence',
    description: 'Real-time hiring signals and offshore potential analysis',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased font-sans bg-gray-50 text-gray-900 min-h-screen">
        {children}
      </body>
    </html>
  );
}
