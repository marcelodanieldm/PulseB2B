/**
 * Main Dashboard Page
 * Global Opportunities Map with Traffic Light System
 */

'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Grid, Map as MapIcon, Loader2 } from 'lucide-react';

import OpportunitiesMap from '@/components/OpportunitiesMap';
import CompanyCard from '@/components/CompanyCard';
import GrowthChart from '@/components/GrowthChart';
import FilterPanel from '@/components/FilterPanel';
import DashboardStatsCards from '@/components/DashboardStats';
import { Company, MapFilters, DashboardStats, GrowthMetrics } from '@/types';
import { getTrafficLightStatus, sortCompaniesByPriority } from '@/lib/utils';

export default function DashboardPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [viewMode, setViewMode] = useState<'map' | 'grid'>('map');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  // Filters
  const [filters, setFilters] = useState<MapFilters>({
    status: [],
    minProbability: 0,
    maxProbability: 100,
    regions: [],
    fundingStages: [],
    minFunding: 0,
    maxFunding: 100000000,
  });

  // Load companies (mock data for now)
  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    setIsLoading(true);
    try {
      // TODO: Replace with actual API call to Supabase
      // const { data, error } = await supabase.from('hiring_predictions').select('*')
      
      // Mock data for demonstration
      const mockCompanies: Company[] = generateMockCompanies(50);
      setCompanies(mockCompanies);
    } catch (error) {
      console.error('Error loading companies:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate dashboard stats
  const dashboardStats: DashboardStats = {
    totalCompanies: companies.length,
    highProbabilityCount: companies.filter(c => c.hiring_probability >= 70).length,
    recentFundingCount: companies.filter(c => c.status === 'golden').length,
    atRiskCount: companies.filter(c => c.status === 'red').length,
    averageProbability: companies.reduce((sum, c) => sum + c.hiring_probability, 0) / companies.length || 0,
    totalActiveJobs: companies.reduce((sum, c) => sum + c.active_job_posts, 0),
    avgJobVelocity: companies.reduce((sum, c) => sum + c.job_post_velocity, 0) / companies.length || 0,
    hotLeadsCount: companies.filter(c => c.hiring_probability >= 80).length,
    conversionRate: 15.3, // Mock value
    totalConversions: 23, // Mock value
    newCompaniesThisWeek: 12, // Mock value
    totalRecentFunding: companies.filter(c => c.status === 'golden').reduce((sum, c) => sum + c.total_funding, 0),
  };

  // Search and filter
  const filteredCompanies = companies
    .filter((company) => {
      // Search query
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          company.name.toLowerCase().includes(query) ||
          company.city.toLowerCase().includes(query) ||
          company.country.toLowerCase().includes(query)
        );
      }
      return true;
    })
    .sort((a, b) => sortCompaniesByPriority(a, b));

  const resetFilters = () => {
    setFilters({
      status: [],
      minProbability: 0,
      maxProbability: 100,
      regions: [],
      fundingStages: [],
      minFunding: 0,
      maxFunding: 100000000,
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
        <div className="text-center">
          <Loader2 className="w-16 h-16 text-indigo-600 animate-spin mx-auto mb-4" />
          <p className="text-lg font-semibold text-gray-700">Loading opportunities...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      {/* Header */}
      <header className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-[1920px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                PulseB2B
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Global IT Hiring Opportunities Dashboard
              </p>
            </div>

            {/* Search Bar */}
            <div className="flex-1 max-w-2xl mx-8">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search companies, cities, countries..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 rounded-xl border-2 border-gray-200 focus:border-indigo-500 focus:outline-none transition-colors"
                />
              </div>
            </div>

            {/* View Mode Toggle */}
            <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('map')}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center space-x-2 ${
                  viewMode === 'map'
                    ? 'bg-white text-indigo-600 shadow-md'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <MapIcon className="w-4 h-4" />
                <span>Map</span>
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center space-x-2 ${
                  viewMode === 'grid'
                    ? 'bg-white text-indigo-600 shadow-md'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Grid className="w-4 h-4" />
                <span>Grid</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1920px] mx-auto px-6 py-6">
        {/* Dashboard Stats */}
        <div className="mb-6">
          <DashboardStatsCards stats={dashboardStats} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <FilterPanel
              filters={filters}
              onFiltersChange={setFilters}
              onReset={resetFilters}
            />
          </div>

          {/* Main View */}
          <div className="lg:col-span-3 space-y-6">
            {/* Map View */}
            {viewMode === 'map' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="h-[600px]"
              >
                <OpportunitiesMap
                  companies={filteredCompanies}
                  filters={filters}
                  selectedCompany={selectedCompany}
                  onCompanySelect={setSelectedCompany}
                />
              </motion.div>
            )}

            {/* Grid View */}
            {viewMode === 'grid' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="grid grid-cols-1 xl:grid-cols-2 gap-6"
              >
                {filteredCompanies.map((company) => (
                  <CompanyCard
                    key={company.id}
                    company={company}
                    onClick={() => setSelectedCompany(company)}
                    featured={company.status === 'golden'}
                  />
                ))}
              </motion.div>
            )}

            {/* Selected Company Details */}
            {selectedCompany && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <GrowthChart
                  companyName={selectedCompany.name}
                  metrics={generateMockGrowthMetrics(selectedCompany)}
                />
              </motion.div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

// Helper function to generate mock companies
function generateMockCompanies(count: number): Company[] {
  const cities = [
    { name: 'San Francisco', country: 'USA', lat: 37.7749, lng: -122.4194, region: 'North America' },
    { name: 'New York', country: 'USA', lat: 40.7128, lng: -74.0060, region: 'North America' },
    { name: 'London', country: 'UK', lat: 51.5074, lng: -0.1278, region: 'Europe' },
    { name: 'Berlin', country: 'Germany', lat: 52.5200, lng: 13.4050, region: 'Europe' },
    { name: 'Singapore', country: 'Singapore', lat: 1.3521, lng: 103.8198, region: 'Asia Pacific' },
    { name: 'São Paulo', country: 'Brazil', lat: -23.5505, lng: -46.6333, region: 'South America' },
  ];

  const industries = ['AI/ML', 'FinTech', 'HealthTech', 'E-commerce', 'SaaS', 'Enterprise Software'];
  const fundingStages = ['Seed', 'Series A', 'Series B', 'Series C', 'Series D+'];

  return Array.from({ length: count }, (_, i) => {
    const city = cities[Math.floor(Math.random() * cities.length)];
    const funding_recency = Math.floor(Math.random() * 1000);
    const tech_churn = Math.random() * 30;
    const job_post_velocity = Math.random() * 3;
    const team_size = Math.floor(Math.random() * 500) + 50;
    const senior_departures = Math.floor(Math.random() * 10);
    const total_funding = Math.floor(Math.random() * 50000000) + 1000000;
    const last_funding_date = new Date(Date.now() - funding_recency * 24 * 60 * 60 * 1000).toISOString();

    // Calculate hiring probability (simplified)
    let probability = 50;
    if (funding_recency < 90) probability += 20;
    if (tech_churn < 10) probability += 10;
    if (job_post_velocity > 1.5) probability += 15;
    probability = Math.min(95, Math.max(10, probability + (Math.random() * 20 - 10)));

    const company: Company = {
      id: `company-${i}`,
      name: `Company ${i + 1}`,
      city: city.name,
      country: city.country,
      latitude: city.lat + (Math.random() - 0.5) * 2,
      longitude: city.lng + (Math.random() - 0.5) * 2,
      region: city.region,
      industry: industries[Math.floor(Math.random() * industries.length)],
      team_size: team_size,
      team_size_growth_3m: Math.floor((Math.random() - 0.3) * 50),
      total_funding: total_funding,
      funding_stage: fundingStages[Math.floor(Math.random() * fundingStages.length)],
      last_funding_date: last_funding_date,
      funding_recency: funding_recency,
      active_job_posts: Math.floor(Math.random() * 50),
      job_post_velocity: job_post_velocity,
      tech_churn: tech_churn,
      senior_departures: senior_departures,
      hiring_probability: probability,
      confidence: 0.7 + Math.random() * 0.25,
      label: probability >= 70 ? 'High' : probability >= 40 ? 'Medium' : 'Low',
      last_updated: new Date().toISOString(),
      status: 'blue',
      status_reason: '',
    };

    const statusResult = getTrafficLightStatus(company);
    company.status = statusResult.status;
    company.status_reason = statusResult.reason;

    return company;
  });
}

// Helper function to generate mock growth metrics
function generateMockGrowthMetrics(company: Company): GrowthMetrics {
  const months = 12;
  const timeSeries = Array.from({ length: months }, (_, i) => {
    const date = new Date();
    date.setMonth(date.getMonth() - (months - i - 1));
    return {
      date: date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
      team_size: Math.max(10, company.team_size - Math.floor(Math.random() * 100)),
      funding: company.total_funding * (0.3 + (i / months) * 0.7),
      job_posts: Math.floor(Math.random() * 30) + 5,
    };
  });

  return {
    timeSeries,
    currentTeamSize: company.team_size,
    teamGrowthRate: company.team_size_growth_3m,
    totalFunding: company.total_funding,
    fundingStage: company.funding_stage,
    activeJobs: company.active_job_posts,
    jobVelocity: company.job_post_velocity,
    lastUpdated: company.last_updated,
  };
}
