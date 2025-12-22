'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import RegionalHeatmap from '@/components/RegionalHeatmap';
import RegionSelector from '@/components/RegionSelector';
import GlobalSignalTicker from '@/components/GlobalSignalTicker';
import { SignalTable } from '@/components/SignalTable';
import { UnlockPremiumModal } from '@/components/UnlockPremiumModal';
import { AuthGuard } from '@/components/auth/LoginModal';
import { useAuth } from '@/hooks/useAuth';
import { usePremiumStatus } from '@/hooks/usePremiumStatus';
import { Activity, Globe, TrendingUp, DollarSign, Users, Zap, Crown, Sparkles } from 'lucide-react';

function ContinentalDashboardContent() {
  const [selectedRegion, setSelectedRegion] = useState('all');
  const [sortBy, setSortBy] = useState<'pulse' | 'arbitrage'>('pulse');
  const [heatmapData, setHeatmapData] = useState<Record<string, any>>({});
  const [tableData, setTableData] = useState<any[]>([]);
  const [showPremiumModal, setShowPremiumModal] = useState(false);
  const [stats, setStats] = useState({
    totalLeads: 0,
    criticalLeads: 0,
    avgPulseScore: 0,
    topArbitrageCountry: ''
  });

  // Authentication and premium status
  const { user, isAuthenticated } = useAuth();
  const { isPremium, loading: premiumLoading } = usePremiumStatus();

  // Stripe payment link - replace with your actual link
  const STRIPE_PAYMENT_LINK = process.env.NEXT_PUBLIC_STRIPE_PAYMENT_LINK || 'https://buy.stripe.com/your_link_here';

  // Load data on mount (replace with real API call)
  useEffect(() => {
    loadDashboardData();
  }, [selectedRegion, sortBy]);

  const loadDashboardData = async () => {
    // Mock data - replace with real API call to backend
    // GET /api/continental/leads?region=${selectedRegion}&sortBy=${sortBy}
    
    const mockHeatmapData = {
      'US': { leadCount: 145, avgPulseScore: 82, criticalLeads: 23, arbitrageScore: 45 },
      'CA': { leadCount: 67, avgPulseScore: 78, criticalLeads: 12, arbitrageScore: 52 },
      'MX': { leadCount: 89, avgPulseScore: 75, criticalLeads: 18, arbitrageScore: 88 },
      'BR': { leadCount: 123, avgPulseScore: 79, criticalLeads: 21, arbitrageScore: 85 },
      'AR': { leadCount: 56, avgPulseScore: 73, criticalLeads: 9, arbitrageScore: 92 },
      'CO': { leadCount: 45, avgPulseScore: 71, criticalLeads: 7, arbitrageScore: 86 },
      'CL': { leadCount: 34, avgPulseScore: 69, criticalLeads: 5, arbitrageScore: 81 },
      'PE': { leadCount: 28, avgPulseScore: 68, criticalLeads: 4, arbitrageScore: 84 },
      'UY': { leadCount: 12, avgPulseScore: 65, criticalLeads: 2, arbitrageScore: 78 }
    };

    const mockTableData = [
      {
        id: '1',
        company_name: 'TechCorp USA',
        country_code: 'US',
        pulse_score: 92,
        desperation_level: 'CRITICAL' as const,
        urgency: 'Immediate',
        hiring_probability: 87,
        expansion_density: 85,
        tech_stack: ['React', 'Node.js', 'AWS'],
        funding_amount: 50000000,
        funding_fuzzy_range: '$10M-$50M',
        funding_date: '2024-11-15',
        last_seen: '2024-12-22',
        has_red_flags: false,
        recommendation: 'Strong candidate for immediate outreach',
        company_insight: 'TechCorp USA raised $10M-$50M (backed by Y Combinator) in San Francisco using React, Node.js, AWS. 🔥 Actively hiring - URGENT need detected. Signal: Recent funding round. Team size: ~150.',
        email: isPremium ? 'hiring@techcorp.com' : null,
        phone_number: isPremium ? '+1 (415) 555-0123' : null,
        funding_exact_amount: isPremium ? 50000000 : null
      },
      {
        id: '2',
        company_name: 'DataFlow Brasil',
        country_code: 'BR',
        pulse_score: 88,
        desperation_level: 'CRITICAL' as const,
        urgency: 'High',
        hiring_probability: 82,
        expansion_density: 78,
        tech_stack: ['Python', 'Django', 'PostgreSQL'],
        funding_amount: 30000000,
        funding_fuzzy_range: '$10M-$50M',
        funding_date: '2024-10-28',
        last_seen: '2024-12-21',
        has_red_flags: false,
        recommendation: 'High arbitrage opportunity - lower cost market',
        company_insight: 'DataFlow Brasil raised $10M-$50M in São Paulo using Python, Django, PostgreSQL. 📈 High hiring probability - High urgency signals. 💰 High arbitrage opportunity (8.5/10 savings potential). Signal: Active job posting. Team size: ~85.',
        email: isPremium ? 'rh@dataflow.com.br' : null,
        phone_number: isPremium ? '+55 11 98765-4321' : null,
        funding_exact_amount: isPremium ? 30000000 : null
      },
      {
        id: '3',
        company_name: 'CloudNine Mexico',
        country_code: 'MX',
        pulse_score: 85,
        desperation_level: 'HIGH' as const,
        urgency: 'Moderate',
        hiring_probability: 79,
        expansion_density: 72,
        tech_stack: ['Vue.js', 'Laravel', 'MySQL'],
        funding_amount: 15000000,
        funding_fuzzy_range: '$5M-$10M',
        funding_date: '2024-09-12',
        last_seen: '2024-12-20',
        has_red_flags: false,
        recommendation: 'Excellent cost-benefit ratio',
        company_insight: 'CloudNine Mexico raised $5M-$10M in Mexico City using Vue.js, Laravel, MySQL. 👀 Exploring candidates - Moderate urgency. 💰 High arbitrage opportunity (9.0/10 savings potential). Signal: Tech stack migration. Team size: ~45.',
        email: isPremium ? 'talent@cloudnine.mx' : null,
        phone_number: isPremium ? '+52 55 1234 5678' : null,
        funding_exact_amount: isPremium ? 15000000 : null
      },
      {
        id: '4',
        company_name: 'SecureNet Argentina',
        country_code: 'AR',
        pulse_score: 81,
        desperation_level: 'HIGH' as const,
        urgency: 'Moderate',
        hiring_probability: 75,
        expansion_density: 68,
        tech_stack: ['Angular', 'Java', 'Oracle'],
        funding_amount: 8000000,
        funding_fuzzy_range: '$5M-$10M',
        funding_date: '2024-08-05',
        last_seen: '2024-12-19',
        has_red_flags: false,
        recommendation: 'Premium arbitrage opportunity',
        company_insight: 'SecureNet Argentina raised $5M-$10M in Buenos Aires using Angular, Java, Oracle. 👀 Exploring candidates. 💰 Premium arbitrage opportunity (9.2/10 savings potential). Signal: GitHub activity spike. Team size: ~35.',
        email: isPremium ? 'jobs@securenet.com.ar' : null,
        phone_number: isPremium ? '+54 11 4567 8900' : null,
        funding_exact_amount: isPremium ? 8000000 : null
      }
    ];

    setHeatmapData(mockHeatmapData);
    setTableData(mockTableData);
    
    // Calculate stats
    const total = Object.values(mockHeatmapData).reduce((sum, country) => sum + country.leadCount, 0);
    const critical = Object.values(mockHeatmapData).reduce((sum, country) => sum + country.criticalLeads, 0);
    const avgScore = Object.values(mockHeatmapData).reduce((sum, country) => sum + country.avgPulseScore, 0) / Object.values(mockHeatmapData).length;
    const topArbitrage = Object.entries(mockHeatmapData).sort((a, b) => (b[1].arbitrageScore || 0) - (a[1].arbitrageScore || 0))[0];

    setStats({
      totalLeads: total,
      criticalLeads: critical,
      avgPulseScore: Math.round(avgScore),
      topArbitrageCountry: topArbitrage[0]
    });
  };

  const regionStats = {
    all: { leadCount: stats.totalLeads, criticalLeads: stats.criticalLeads },
    north_america: { leadCount: 212, criticalLeads: 35 },
    central_america: { leadCount: 89, criticalLeads: 18 },
    andean_region: { leadCount: 73, criticalLeads: 11 },
    southern_cone: { leadCount: 225, criticalLeads: 37 }
  };

  return (
    <div className="min-h-screen bg-[#0A0E1A]">
      {/* Global Signal Ticker */}
      <GlobalSignalTicker />

      {/* Header */}
      <div className="border-b border-gray-800 bg-gradient-to-b from-gray-950 to-transparent">
        <div className="container mx-auto px-6 py-6">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-between"
          >
            <div>
              <div className="flex items-center gap-3 mb-2">
                <Globe className="w-8 h-8 text-blue-500" />
                <h1 className="text-3xl font-bold text-white">
                  Continental Command Center
                </h1>
                {isPremium && (
                  <span className="px-3 py-1 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-xs font-bold rounded-full flex items-center gap-1.5">
                    <Crown className="w-3 h-3" />
                    PREMIUM
                  </span>
                )}
              </div>
              <p className="text-gray-400 text-sm">
                Real-time intelligence from Canada to Argentina • 19 Countries • $0 Infrastructure Cost
              </p>
            </div>
            
            {/* Quick stats */}
            <div className="flex items-center gap-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-white">{stats.totalLeads}</p>
                <p className="text-xs text-gray-500">Active Leads</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-red-400">{stats.criticalLeads}</p>
                <p className="text-xs text-gray-500">Critical</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-blue-400">{stats.avgPulseScore}</p>
                <p className="text-xs text-gray-500">Avg Score</p>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Main content */}
      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Left sidebar - Region selector */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="col-span-3"
          >
            <div className="bg-gray-950 border border-gray-800 rounded-xl p-6 sticky top-6">
              <RegionSelector
                selectedRegion={selectedRegion}
                onRegionChange={setSelectedRegion}
                stats={regionStats}
              />

              {/* Sort options */}
              <div className="mt-6 pt-6 border-t border-gray-800">
                <h4 className="text-xs font-bold text-gray-500 uppercase mb-3">
                  Cost-Benefit Filter
                </h4>
                <div className="space-y-2">
                  <button
                    onClick={() => setSortBy('pulse')}
                    className={`
                      w-full px-4 py-2 rounded-lg text-sm font-medium transition-all
                      ${sortBy === 'pulse'
                        ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                        : 'bg-gray-900 text-gray-400 border border-gray-800 hover:border-gray-700'
                      }
                    `}
                  >
                    <Zap className="w-4 h-4 inline mr-2" />
                    Highest Pulse Score
                  </button>
                  <button
                    onClick={() => setSortBy('arbitrage')}
                    className={`
                      w-full px-4 py-2 rounded-lg text-sm font-medium transition-all
                      ${sortBy === 'arbitrage'
                        ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                        : 'bg-gray-900 text-gray-400 border border-gray-800 hover:border-gray-700'
                      }
                    `}
                  >
                    <DollarSign className="w-4 h-4 inline mr-2" />
                    Best Arbitrage Score
                  </button>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Center - Heatmap */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="col-span-6"
          >
            <div className="bg-gray-950 border border-gray-800 rounded-xl overflow-hidden">
              {/* Heatmap header */}
              <div className="px-6 py-4 border-b border-gray-800 bg-gray-900/50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="w-5 h-5 text-blue-500" />
                    <h2 className="text-lg font-bold text-white">Regional Heatmap</h2>
                  </div>
                  <span className="text-xs text-gray-500">
                    {selectedRegion === 'all' ? 'All Regions' : selectedRegion.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
              </div>

              {/* Heatmap */}
              <div className="p-6" style={{ minHeight: '700px' }}>
                <RegionalHeatmap
                  data={heatmapData}
                  selectedRegion={selectedRegion}
                  onCountryClick={(code) => console.log('Clicked:', code)}
                />
              </div>
            </div>
          </motion.div>

          {/* Right sidebar - Key insights */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="col-span-3"
          >
            <div className="space-y-4 sticky top-6">
              {/* Top arbitrage opportunity */}
              <div className="bg-gradient-to-br from-green-500/10 to-green-500/5 border border-green-500/30 rounded-xl p-6">
                <div className="flex items-center gap-2 mb-3">
                  <DollarSign className="w-5 h-5 text-green-400" />
                  <h3 className="text-sm font-bold text-green-400 uppercase">Top Arbitrage</h3>
                </div>
                <p className="text-3xl font-bold text-white mb-2">{stats.topArbitrageCountry}</p>
                <p className="text-xs text-gray-400">Highest cost-benefit ratio for hiring</p>
              </div>

              {/* Market pulse */}
              <div className="bg-gray-950 border border-gray-800 rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp className="w-5 h-5 text-blue-500" />
                  <h3 className="text-sm font-bold text-gray-400 uppercase">Market Pulse</h3>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500">North America</span>
                    <span className="text-sm font-bold text-blue-400">High</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500">LATAM</span>
                    <span className="text-sm font-bold text-green-400">Moderate</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500">Brazil</span>
                    <span className="text-sm font-bold text-amber-400">Growing</span>
                  </div>
                </div>
              </div>

              {/* Live activity */}
              <div className="bg-gray-950 border border-gray-800 rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Users className="w-5 h-5 text-purple-500" />
                  <h3 className="text-sm font-bold text-gray-400 uppercase">Live Activity</h3>
                </div>
                <div className="space-y-3 text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                    <span className="text-gray-400">12 new leads (US, BR)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
                    <span className="text-gray-400">5 funding updates</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                    <span className="text-gray-400">3 critical alerts</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Table section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-8"
        >
          <div className="bg-gray-950 border border-gray-800 rounded-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-800 bg-gray-900/50">
              <h2 className="text-lg font-bold text-white">
                {sortBy === 'arbitrage' ? 'Best Cost-Benefit Opportunities' : 'Highest Priority Leads'}
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                Showing {tableData.length} companies across {selectedRegion === 'all' ? '19 countries' : selectedRegion.replace('_', ' ')}
              </p>
            </div>
            <SignalTable 
              data={tableData} 
              isPremium={isPremium} 
              onUpgrade={() => setShowPremiumModal(true)} 
            />
          </div>
        </motion.div>
      </div>

      {/* Unlock Premium Modal */}
      <UnlockPremiumModal
        isOpen={showPremiumModal}
        onClose={() => setShowPremiumModal(false)}
        stripePaymentLink={STRIPE_PAYMENT_LINK}
      />
    </div>
  );
}

// Main export with AuthGuard wrapper
export default function ContinentalDashboard() {
  return (
    <AuthGuard>
      <ContinentalDashboardContent />
    </AuthGuard>
  );
}
