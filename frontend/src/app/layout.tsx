/**
 * Root Layout
 * Global styles and providers
 */

import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'PulseB2B - Global IT Hiring Opportunities',
  description: 'ML-powered platform for discovering IT hiring opportunities with traffic light system',
  keywords: 'IT hiring, recruitment, ML predictions, B2B, opportunities',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}
