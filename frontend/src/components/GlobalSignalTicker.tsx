'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { COUNTRY_FLAGS } from '@/lib/americasMapData';

interface FundingSignal {
  id: string;
  company: string;
  country: string;
  countryCode: string;
  fundingAmount: string;
  pulseScore: number;
  timestamp: string;
  summary: string;
  isBreaking?: boolean;
}

interface GlobalSignalTickerProps {
  signals?: FundingSignal[];
  speed?: number; // pixels per second
}

export default function GlobalSignalTicker({ 
  signals = [],
  speed = 50 
}: GlobalSignalTickerProps) {
  const tickerRef = useRef<HTMLDivElement>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState<number | null>(null);

  // Mock data if no signals provided
  const defaultSignals: FundingSignal[] = [
    {
      id: '1',
      company: 'TechCorp',
      country: 'United States',
      countryCode: 'US',
      fundingAmount: '$50M Series B',
      pulseScore: 92,
      timestamp: '5 min ago',
      summary: 'AI-powered analytics platform raises Series B',
      isBreaking: true
    },
    {
      id: '2',
      company: 'DataFlow',
      country: 'Brazil',
      countryCode: 'BR',
      fundingAmount: 'R$30M Series A',
      pulseScore: 85,
      timestamp: '12 min ago',
      summary: 'Cloud infrastructure startup expands LATAM operations'
    },
    {
      id: '3',
      company: 'CloudNine',
      country: 'Mexico',
      countryCode: 'MX',
      fundingAmount: '$15M Seed',
      pulseScore: 78,
      timestamp: '23 min ago',
      summary: 'Fintech platform targets SMB market'
    },
    {
      id: '4',
      company: 'SecureNet',
      country: 'Argentina',
      countryCode: 'AR',
      fundingAmount: '$8M Series A',
      pulseScore: 88,
      timestamp: '35 min ago',
      summary: 'Cybersecurity firm announces regional expansion'
    },
    {
      id: '5',
      company: 'InnovateAI',
      country: 'Colombia',
      countryCode: 'CO',
      fundingAmount: '$12M Seed',
      pulseScore: 81,
      timestamp: '42 min ago',
      summary: 'Machine learning startup opens Bogotá office'
    },
    {
      id: '6',
      company: 'DevOps Pro',
      country: 'Chile',
      countryCode: 'CL',
      fundingAmount: '$6M Seed',
      pulseScore: 75,
      timestamp: '1 hour ago',
      summary: 'DevOps automation platform secures funding'
    }
  ];

  const displaySignals = signals.length > 0 ? signals : defaultSignals;

  // Duplicate signals for seamless loop
  const extendedSignals = [...displaySignals, ...displaySignals];

  return (
    <div className="relative w-full overflow-hidden bg-gray-950 border-y border-gray-800">
      {/* Breaking news indicator */}
      <div className="absolute left-0 top-0 bottom-0 z-20 bg-gradient-to-r from-red-500 to-transparent w-32 flex items-center justify-start pl-4">
        <motion.div
          animate={{ opacity: [1, 0.5, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="flex items-center gap-2"
        >
          <div className="w-2 h-2 rounded-full bg-red-500"></div>
          <span className="text-xs font-bold text-white uppercase tracking-wider">
            Live
          </span>
        </motion.div>
      </div>

      {/* Ticker container */}
      <div 
        className="relative py-3"
        onMouseEnter={() => setIsPaused(true)}
        onMouseLeave={() => {
          setIsPaused(false);
          setHighlightedIndex(null);
        }}
      >
        <motion.div
          ref={tickerRef}
          className="flex gap-8 items-center"
          animate={{
            x: isPaused ? undefined : [0, -(displaySignals.length * 400)]
          }}
          transition={{
            x: {
              duration: displaySignals.length * (400 / speed),
              repeat: Infinity,
              ease: "linear"
            }
          }}
          style={{ x: 0 }}
        >
          {extendedSignals.map((signal, index) => (
            <motion.div
              key={`${signal.id}-${index}`}
              className={`
                flex items-center gap-3 px-6 py-2 rounded-lg transition-all cursor-pointer
                ${highlightedIndex === index 
                  ? 'bg-gray-800 shadow-lg scale-105' 
                  : 'bg-transparent'
                }
              `}
              whileHover={{ scale: 1.05 }}
              onHoverStart={() => setHighlightedIndex(index)}
              style={{ minWidth: '400px' }}
            >
              {/* Flag */}
              <span className="text-2xl flex-shrink-0">
                {COUNTRY_FLAGS[signal.countryCode] || '🌎'}
              </span>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-bold text-white text-sm truncate">
                    {signal.company}
                  </span>
                  {signal.isBreaking && (
                    <span className="px-2 py-0.5 bg-red-500 text-white text-xs font-bold rounded uppercase">
                      New
                    </span>
                  )}
                </div>
                
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-green-400 font-semibold">
                    {signal.fundingAmount}
                  </span>
                  <span className="text-gray-600">•</span>
                  <span className="text-gray-400 truncate">
                    {signal.summary}
                  </span>
                </div>
              </div>

              {/* Pulse score badge */}
              <div className={`
                flex-shrink-0 px-3 py-1 rounded-full text-xs font-bold
                ${signal.pulseScore >= 85 
                  ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                  : signal.pulseScore >= 70
                  ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                  : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                }
              `}>
                {signal.pulseScore}
              </div>

              {/* Timestamp */}
              <span className="text-xs text-gray-600 flex-shrink-0">
                {signal.timestamp}
              </span>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Fade gradient edges */}
      <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-gray-950 to-transparent pointer-events-none z-10"></div>
      <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-gray-950 to-transparent pointer-events-none z-10"></div>

      {/* Pause indicator */}
      <AnimatePresence>
        {isPaused && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-1 right-4 px-2 py-1 bg-gray-800 rounded text-xs text-gray-400 z-20"
          >
            Paused - Hover to explore
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
