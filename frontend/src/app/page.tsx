/**
 * Premium Global Dashboard
 * Market Intelligence Platform for US, Brazil, and Mexico Ventures
 */

'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Globe, 
  TrendingUp, 
  Zap, 
  Target, 
  Search,
  Filter,
  Download,
  RefreshCw,
  BarChart3,
  Lock
} from 'lucide-react';

import GlobalSignalMap from '@/components/GlobalSignalMap';
import PremiumPaywall from '@/components/PremiumPaywall';
import { Company } from '@/types';
import { createClient } from '@/lib/supabase';
import { formatCurrency, formatPercentage } from '@/lib/utils';

export default function PremiumDashboard() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isPremium, setIsPremium] = useState(false); // TODO: Check auth status
  const [showPaywall, setShowPaywall] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  // Load ventures from Supabase
  useEffect(() => {
    loadVentures();
  }, []);

  const loadVentures = async () => {
    setIsLoading(true);
    try {
      const supabase = createClient();
      
      // Try to load from oracle_predictions first (Oracle data)
      const { data: oracleData, error: oracleError } = await supabase
        .from('oracle_predictions')
        .select('*')
        .order('hiring_probability', { ascending: false });

      if (oracleData && oracleData.length > 0) {
        // Transform Oracle data to Company type
        const transformedCompanies = oracleData.map((row: any, idx: number) => ({
          id: row.id?.toString() || `oracle-${idx}`,
          name: row.company_name,
          region: row.country === 'USA' ? 'North America' : 'Latin America',
          country: row.country || 'USA',
          city: row.city || 'Unknown',
          latitude: row.latitude || getCountryDefaultLat(row.country),
          longitude: row.longitude || getCountryDefaultLon(row.country),
          team_size: row.team_size || estimateTeamSize(row.estimated_amount_millions),
          total_funding: row.estimated_amount_millions || 0,
          last_funding_amount: row.estimated_amount_millions || 0,
          last_funding_date: row.funding_date,
          funding_stage: determineFundingStage(row.estimated_amount_millions),
          hiring_probability: row.hiring_probability,
          confidence: row.hiring_probability >= 85 ? 'HIGH' : row.hiring_probability >= 70 ? 'MEDIUM' : 'LOW',
          prediction_label: row.hiring_probability >= 70 ? 'LIKELY' : 'POSSIBLE',
          status: determineStatus(row),
          status_reason: `${row.hiring_signals || 0} hiring signals detected`,
          funding_recency: row.days_since_filing || 0,
          tech_churn: 0,
          job_post_velocity: (row.hiring_signals || 0) / 10,
          region_factor: 1.0,
          senior_departures: 0,
          current_month_posts: row.hiring_signals || 0,
          website: row.website || '',
          description: row.description || '',
          predicted_at: row.created_at,
          updated_at: row.updated_at || row.created_at,
        }));

        setCompanies(transformedCompanies);
        setLastUpdated(new Date());
      } else {
        // Fallback to mock data
        const mockCompanies = generateMockVentures(100);
        setCompanies(mockCompanies);
      }
    } catch (error) {
      console.error('Error loading ventures:', error);
      // Load mock data on error
      const mockCompanies = generateMockVentures(100);
      setCompanies(mockCompanies);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper functions
  const getCountryDefaultLat = (country: string) => {
    const defaults: Record<string, number> = {
      'USA': 37.0902,
      'United States': 37.0902,
      'Brazil': -15.7801,
      'Brasil': -15.7801,
      'Mexico': 23.6345,
      'México': 23.6345,
    };
    return defaults[country] || 0;
  };

  const getCountryDefaultLon = (country: string) => {
    const defaults: Record<string, number> = {
      'USA': -95.7129,
      'United States': -95.7129,
      'Brazil': -47.9292,
      'Brasil': -47.9292,
      'Mexico': -102.5528,
      'México': -102.5528,
    };
    return defaults[country] || 0;
  };

  const estimateTeamSize = (fundingMillions: number | null) => {
    if (!fundingMillions) return 20;
    if (fundingMillions >= 100) return 250;
    if (fundingMillions >= 50) return 150;
    if (fundingMillions >= 20) return 80;
    return 30;
  };

  const determineFundingStage = (fundingMillions: number | null) => {
    if (!fundingMillions) return 'Seed';
    if (fundingMillions >= 50) return 'Series B+';
    if (fundingMillions >= 20) return 'Series A';
    return 'Seed';
  };

  const determineStatus = (row: any) => {
    if (row.hiring_probability >= 85) return 'golden';
    if (row.hiring_probability >= 70) return 'green';
    if (row.hiring_probability >= 50) return 'blue';
    return 'red';
  };

  // Filter companies by search
  const filteredCompanies = companies.filter((company) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      company.name.toLowerCase().includes(query) ||
      company.city.toLowerCase().includes(query) ||
      company.country.toLowerCase().includes(query)
    );
  });

  // Calculate stats
  const stats = {
    totalVentures: filteredCompanies.length,
    criticalSignals: filteredCompanies.filter(c => c.hiring_probability >= 85).length,
    highPotential: filteredCompanies.filter(c => c.hiring_probability >= 70 && c.hiring_probability < 85).length,
    totalRunway: filteredCompanies.reduce((sum, c) => sum + c.total_funding, 0),
    avgScalability: filteredCompanies.reduce((sum, c) => sum + c.job_post_velocity, 0) / filteredCompanies.length || 0,
  };

  // Handle export
  const handleExport = () => {
    if (!isPremium) {
      setShowPaywall(true);
      return;
    }
    // TODO: Implement CSV export
    alert('Export feature coming soon!');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white/80 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-[1920px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl">
                <Globe className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">PulseB2B</h1>
                <p className="text-xs text-gray-600">Global Market Intelligence</p>
              </div>
            </div>

            {/* Search */}
            <div className="flex-1 max-w-md mx-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search ventures, locations..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3">
              <button
                onClick={loadVentures}
                disabled={isLoading}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 flex items-center gap-2 transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </button>

              <button
                onClick={handleExport}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 flex items-center gap-2 transition-colors"
              >
                <Download className="w-4 h-4" />
                Export
              </button>

              {!isPremium && (
                <button
                  onClick={() => setShowPaywall(true)}
                  className="px-5 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg flex items-center gap-2"
                >
                  <Lock className="w-4 h-4" />
                  Upgrade to Premium
                </button>
              )}
            </div>
          </div>

          {/* Last Updated */}
          <div className="mt-3 text-xs text-gray-600">
            Last updated: {lastUpdated.toLocaleString('en-US', { 
              month: 'short', 
              day: 'numeric', 
              year: 'numeric', 
              hour: '2-digit', 
              minute: '2-digit' 
            })} • Automated via GitHub Actions (12h cycle)
          </div>
        </div>
      </header>

      {/* Stats Bar */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-[1920px] mx-auto px-6 py-6">
          <div className="grid grid-cols-5 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center"
            >
              <div className="text-3xl font-bold text-gray-900">{stats.totalVentures}</div>
              <div className="text-sm text-gray-600 flex items-center justify-center gap-1 mt-1">
                <Globe className="w-4 h-4" />
                Active Ventures
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-center"
            >
              <div className="text-3xl font-bold text-green-600">{stats.criticalSignals}</div>
              <div className="text-sm text-gray-600 flex items-center justify-center gap-1 mt-1">
                <Zap className="w-4 h-4" />
                Critical Signals
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-center"
            >
              <div className="text-3xl font-bold text-amber-600">{stats.highPotential}</div>
              <div className="text-sm text-gray-600 flex items-center justify-center gap-1 mt-1">
                <Target className="w-4 h-4" />
                High Potential
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-center"
            >
              <div className="text-3xl font-bold text-blue-600">
                {formatCurrency(stats.totalRunway / 1000, 1)}B
              </div>
              <div className="text-sm text-gray-600 flex items-center justify-center gap-1 mt-1">
                <BarChart3 className="w-4 h-4" />
                Total Runway
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-center"
            >
              <div className="text-3xl font-bold text-purple-600">
                {stats.avgScalability.toFixed(1)}x
              </div>
              <div className="text-sm text-gray-600 flex items-center justify-center gap-1 mt-1">
                <TrendingUp className="w-4 h-4" />
                Avg Scalability
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-[1920px] mx-auto px-6 py-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="h-[calc(100vh-280px)] min-h-[600px]"
        >
          {isLoading ? (
            <div className="h-full flex items-center justify-center bg-white rounded-2xl shadow-xl">
              <div className="text-center">
                <RefreshCw className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
                <p className="text-gray-600 font-medium">Loading global ventures...</p>
              </div>
            </div>
          ) : (
            <GlobalSignalMap
              companies={filteredCompanies}
              onCompanySelect={setSelectedCompany}
              isPremium={isPremium}
              onUnlockClick={() => setShowPaywall(true)}
            />
          )}
        </motion.div>
      </main>

      {/* Premium Paywall Modal */}
      <PremiumPaywall 
        isOpen={showPaywall} 
        onClose={() => setShowPaywall(false)} 
      />
    </div>
  );
}


// Mock data generator for testing
function generateMockVentures(count: number): Company[] {
  const countries = [
    { name: 'USA', lat: 37.0902, lon: -95.7129, cities: ['San Francisco', 'New York', 'Austin', 'Seattle', 'Boston'] },
    { name: 'Brazil', lat: -15.7801, lon: -47.9292, cities: ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília'] },
    { name: 'Mexico', lat: 23.6345, lon: -102.5528, cities: ['Mexico City', 'Guadalajara', 'Monterrey', 'Puebla'] },
  ];

  const ventures: Company[] = [];

  for (let i = 0; i < count; i++) {
    const country = countries[i % countries.length];
    const city = country.cities[Math.floor(Math.random() * country.cities.length)];
    const funding = Math.random() * 200;
    const probability = Math.random() * 100;

    ventures.push({
      id: `venture-${i}`,
      name: `${city} Venture ${i + 1}`,
      region: country.name === 'USA' ? 'North America' : 'Latin America',
      country: country.name,
      city,
      latitude: country.lat + (Math.random() - 0.5) * 10,
      longitude: country.lon + (Math.random() - 0.5) * 10,
      team_size: Math.floor(50 + Math.random() * 200),
      total_funding: funding,
      last_funding_amount: funding * 0.4,
      last_funding_date: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
      funding_stage: funding >= 50 ? 'Series B+' : funding >= 20 ? 'Series A' : 'Seed',
      hiring_probability: probability,
      confidence: probability >= 70 ? 'HIGH' : 'MEDIUM',
      prediction_label: probability >= 70 ? 'LIKELY' : 'POSSIBLE',
      status: probability >= 85 ? 'golden' : probability >= 70 ? 'green' : probability >= 50 ? 'blue' : 'red',
      status_reason: `${Math.floor(probability / 10)} hiring signals detected`,
      funding_recency: Math.floor(Math.random() * 365),
      tech_churn: Math.random() * 20,
      job_post_velocity: Math.random() * 3,
      region_factor: 1.0,
      senior_departures: Math.floor(Math.random() * 5),
      current_month_posts: Math.floor(Math.random() * 20),
      website: `https://${city.toLowerCase().replace(' ', '')}-venture${i + 1}.com`,
      predicted_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });
  }

  return ventures;
}

