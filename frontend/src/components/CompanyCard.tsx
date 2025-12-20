/**
 * Company Card Component
 * Display company information with traffic light status
 */

'use client';

import { motion } from 'framer-motion';
import {
  Building2,
  MapPin,
  DollarSign,
  Users,
  TrendingUp,
  Calendar,
  Zap,
  AlertCircle,
  Star,
} from 'lucide-react';

import { Company } from '@/types';
import {
  getStatusColor,
  getStatusEmoji,
  formatCurrency,
  formatPercentage,
  formatRelativeDate,
} from '@/lib/utils';

interface CompanyCardProps {
  company: Company;
  onClick?: () => void;
  featured?: boolean;
}

export default function CompanyCard({ company, onClick, featured = false }: CompanyCardProps) {
  const statusColor = getStatusColor(company.status);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02, y: -4 }}
      transition={{ duration: 0.2 }}
      onClick={onClick}
      className={`relative bg-white rounded-xl shadow-lg hover:shadow-2xl cursor-pointer overflow-hidden border-2 transition-all ${
        featured ? 'border-yellow-400' : 'border-transparent'
      }`}
      style={{
        borderLeftWidth: '6px',
        borderLeftColor: statusColor,
      }}
    >
      {/* Featured Badge */}
      {featured && (
        <div className="absolute top-3 right-3 bg-yellow-400 text-yellow-900 px-3 py-1 rounded-full text-xs font-bold flex items-center space-x-1 animate-bounce-slow">
          <Star className="w-3 h-3" />
          <span>Destacada</span>
        </div>
      )}

      {/* Status Pulse for Golden */}
      {company.status === 'golden' && (
        <div
          className="absolute top-0 right-0 w-32 h-32 opacity-20 animate-ping-slow"
          style={{
            background: `radial-gradient(circle, ${statusColor} 0%, transparent 70%)`,
          }}
        />
      )}

      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-1">
              <Building2 className="w-5 h-5 text-gray-400" />
              <h3 className="text-xl font-bold text-gray-900 truncate">
                {company.name}
              </h3>
            </div>
            <div className="flex items-center space-x-1 text-sm text-gray-500">
              <MapPin className="w-4 h-4" />
              <span>{company.city}, {company.country}</span>
            </div>
          </div>

          {/* Status Badge */}
          <div
            className="flex flex-col items-center justify-center w-16 h-16 rounded-full border-4 border-white shadow-lg"
            style={{ backgroundColor: statusColor }}
          >
            <span className="text-2xl">{getStatusEmoji(company.status)}</span>
          </div>
        </div>

        {/* Probability Meter */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Probabilidad de Contratación
            </span>
            <span
              className="text-2xl font-bold"
              style={{ color: statusColor }}
            >
              {company.hiring_probability.toFixed(1)}%
            </span>
          </div>
          <div className="relative h-3 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${company.hiring_probability}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className="absolute h-full rounded-full"
              style={{ backgroundColor: statusColor }}
            />
            {/* Gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
          </div>
          <p className="mt-2 text-xs text-gray-500 italic">
            Confianza: {formatPercentage(company.confidence)}
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-3 rounded-lg">
            <div className="flex items-center space-x-2 mb-1">
              <DollarSign className="w-4 h-4 text-green-600" />
              <span className="text-xs font-medium text-gray-600">Funding Total</span>
            </div>
            <p className="text-lg font-bold text-gray-900">
              {formatCurrency(company.total_funding)}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {company.funding_stage} · {formatRelativeDate(company.last_funding_date)}
            </p>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-3 rounded-lg">
            <div className="flex items-center space-x-2 mb-1">
              <Users className="w-4 h-4 text-blue-600" />
              <span className="text-xs font-medium text-gray-600">Team Size</span>
            </div>
            <p className="text-lg font-bold text-gray-900">
              {company.team_size}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Δ {company.team_size_growth_3m > 0 ? '+' : ''}
              {company.team_size_growth_3m} (3m)
            </p>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-3 rounded-lg">
            <div className="flex items-center space-x-2 mb-1">
              <TrendingUp className="w-4 h-4 text-purple-600" />
              <span className="text-xs font-medium text-gray-600">Job Velocity</span>
            </div>
            <p className="text-lg font-bold text-gray-900">
              {company.job_post_velocity.toFixed(2)}x
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {company.active_job_posts} jobs activos
            </p>
          </div>

          <div className="bg-gradient-to-br from-orange-50 to-red-50 p-3 rounded-lg">
            <div className="flex items-center space-x-2 mb-1">
              <Zap className="w-4 h-4 text-orange-600" />
              <span className="text-xs font-medium text-gray-600">Tech Churn</span>
            </div>
            <p className="text-lg font-bold text-gray-900">
              {formatPercentage(company.tech_churn / 100)}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {company.senior_departures} seniors salieron
            </p>
          </div>
        </div>

        {/* Status Reason */}
        <div
          className="p-3 rounded-lg flex items-start space-x-2"
          style={{ backgroundColor: `${statusColor}15` }}
        >
          <AlertCircle
            className="w-4 h-4 mt-0.5 flex-shrink-0"
            style={{ color: statusColor }}
          />
          <p className="text-sm text-gray-700 flex-1">
            <span className="font-semibold">Análisis:</span> {company.status_reason}
          </p>
        </div>

        {/* Tags */}
        <div className="mt-4 flex flex-wrap gap-2">
          <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
            {company.region}
          </span>
          <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
            {company.industry}
          </span>
          {company.hiring_probability >= 80 && (
            <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full font-semibold">
              🔥 Hot Lead
            </span>
          )}
          {company.status === 'golden' && (
            <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full font-semibold animate-pulse">
              ✨ Fresh Funding
            </span>
          )}
        </div>
      </div>

      {/* Footer Actions */}
      <div className="px-6 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
        <div className="flex items-center space-x-1 text-xs text-gray-500">
          <Calendar className="w-3 h-3" />
          <span>Updated {formatRelativeDate(company.last_updated)}</span>
        </div>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onClick?.();
          }}
          className="text-sm font-medium text-indigo-600 hover:text-indigo-800 transition-colors"
        >
          Ver Detalles →
        </button>
      </div>
    </motion.div>
  );
}
