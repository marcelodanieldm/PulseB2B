/**
 * Dashboard Stats Component
 * Overview statistics cards
 */

'use client';

import { motion } from 'framer-motion';
import {
  TrendingUp,
  Building2,
  DollarSign,
  Target,
  Zap,
  Award,
  AlertCircle,
  CheckCircle,
} from 'lucide-react';

import { DashboardStats } from '@/types';
import { formatCurrency } from '@/lib/utils';

interface DashboardStatsProps {
  stats: DashboardStats;
}

export default function DashboardStatsCards({ stats }: DashboardStatsProps) {
  const cards = [
    {
      title: 'Total Companies',
      value: stats.totalCompanies,
      icon: Building2,
      color: 'from-blue-500 to-blue-600',
      change: `+${stats.newCompaniesThisWeek} this week`,
      changeColor: 'text-blue-600',
    },
    {
      title: 'High Probability',
      value: stats.highProbabilityCount,
      icon: Target,
      color: 'from-green-500 to-green-600',
      change: `${((stats.highProbabilityCount / stats.totalCompanies) * 100).toFixed(1)}% of total`,
      changeColor: 'text-green-600',
    },
    {
      title: 'Fresh Funding',
      value: stats.recentFundingCount,
      icon: DollarSign,
      color: 'from-yellow-500 to-yellow-600',
      change: formatCurrency(stats.totalRecentFunding),
      changeColor: 'text-yellow-600',
    },
    {
      title: 'At Risk',
      value: stats.atRiskCount,
      icon: AlertCircle,
      color: 'from-red-500 to-red-600',
      change: `${((stats.atRiskCount / stats.totalCompanies) * 100).toFixed(1)}% of total`,
      changeColor: 'text-red-600',
    },
    {
      title: 'Avg Probability',
      value: `${stats.averageProbability.toFixed(1)}%`,
      icon: TrendingUp,
      color: 'from-purple-500 to-purple-600',
      change: `${stats.averageProbability >= 60 ? '+' : ''}${(stats.averageProbability - 60).toFixed(1)}% vs baseline`,
      changeColor: stats.averageProbability >= 60 ? 'text-green-600' : 'text-red-600',
    },
    {
      title: 'Active Jobs',
      value: stats.totalActiveJobs,
      icon: Briefcase,
      color: 'from-indigo-500 to-indigo-600',
      change: `${stats.avgJobVelocity.toFixed(2)}x avg velocity`,
      changeColor: 'text-indigo-600',
    },
    {
      title: 'Hot Leads',
      value: stats.hotLeadsCount,
      icon: Zap,
      color: 'from-pink-500 to-pink-600',
      change: '≥80% probability',
      changeColor: 'text-pink-600',
    },
    {
      title: 'Conversion Rate',
      value: `${stats.conversionRate.toFixed(1)}%`,
      icon: Award,
      color: 'from-teal-500 to-teal-600',
      change: `${stats.totalConversions} conversions`,
      changeColor: 'text-teal-600',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="relative bg-white rounded-xl shadow-lg p-6 overflow-hidden group hover:shadow-2xl transition-shadow"
          >
            {/* Background Gradient */}
            <div
              className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${card.color} opacity-10 rounded-full -mr-16 -mt-16 group-hover:scale-110 transition-transform`}
            />

            {/* Content */}
            <div className="relative">
              {/* Icon */}
              <div
                className={`inline-flex items-center justify-center w-12 h-12 rounded-lg bg-gradient-to-br ${card.color} mb-4`}
              >
                <Icon className="w-6 h-6 text-white" />
              </div>

              {/* Title */}
              <h3 className="text-sm font-medium text-gray-500 mb-1">
                {card.title}
              </h3>

              {/* Value */}
              <p className="text-3xl font-bold text-gray-900 mb-2">
                {card.value}
              </p>

              {/* Change */}
              <div className="flex items-center space-x-1">
                {card.changeColor.includes('green') ? (
                  <TrendingUp className="w-4 h-4 text-green-600" />
                ) : card.changeColor.includes('red') ? (
                  <TrendingDown className="w-4 h-4 text-red-600" />
                ) : (
                  <CheckCircle className="w-4 h-4 text-gray-400" />
                )}
                <span className={`text-sm font-medium ${card.changeColor}`}>
                  {card.change}
                </span>
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

// Import missing icon
import { Briefcase, TrendingDown } from 'lucide-react';
