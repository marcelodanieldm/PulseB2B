/**
 * Filter Panel Component
 * Advanced filtering for companies and opportunities
 */

'use client';

import { useState } from 'react';
import { Filter, X, ChevronDown, ChevronUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import { MapFilters, TrafficLightStatus } from '@/types';

interface FilterPanelProps {
  filters: MapFilters;
  onFiltersChange: (filters: MapFilters) => void;
  onReset: () => void;
}

export default function FilterPanel({ filters, onFiltersChange, onReset }: FilterPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  const statusOptions: { value: TrafficLightStatus; label: string; color: string; emoji: string }[] = [
    { value: 'green', label: 'Alta Contratación', color: '#10B981', emoji: '🟢' },
    { value: 'golden', label: 'Funding Inminente', color: '#F59E0B', emoji: '🟡' },
    { value: 'red', label: 'Alto Riesgo', color: '#EF4444', emoji: '🔴' },
    { value: 'blue', label: 'Estable', color: '#3B82F6', emoji: '🔵' },
  ];

  const regionOptions = [
    { value: 'North America', label: 'North America' },
    { value: 'South America', label: 'South America' },
    { value: 'Europe', label: 'Europe' },
    { value: 'Asia Pacific', label: 'Asia Pacific' },
  ];

  const fundingStageOptions = [
    { value: 'Pre-Seed', label: 'Pre-Seed' },
    { value: 'Seed', label: 'Seed' },
    { value: 'Series A', label: 'Series A' },
    { value: 'Series B', label: 'Series B' },
    { value: 'Series C', label: 'Series C' },
    { value: 'Series D+', label: 'Series D+' },
  ];

  const handleStatusToggle = (status: TrafficLightStatus) => {
    const newStatus = filters.status.includes(status)
      ? filters.status.filter((s) => s !== status)
      : [...filters.status, status];
    onFiltersChange({ ...filters, status: newStatus });
  };

  const handleRegionToggle = (region: string) => {
    const newRegions = filters.regions.includes(region)
      ? filters.regions.filter((r) => r !== region)
      : [...filters.regions, region];
    onFiltersChange({ ...filters, regions: newRegions });
  };

  const handleFundingStageToggle = (stage: string) => {
    const newStages = filters.fundingStages.includes(stage)
      ? filters.fundingStages.filter((s) => s !== stage)
      : [...filters.fundingStages, stage];
    onFiltersChange({ ...filters, fundingStages: newStages });
  };

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Filter className="w-5 h-5 text-white" />
            <h3 className="text-lg font-bold text-white">Filtros Avanzados</h3>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={onReset}
              className="px-3 py-1 bg-white/20 hover:bg-white/30 text-white text-sm rounded-lg transition-colors flex items-center space-x-1"
            >
              <X className="w-4 h-4" />
              <span>Reset</span>
            </button>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors"
            >
              {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Filter Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="p-6 space-y-6">
              {/* Status Filter */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Traffic Light Status
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {statusOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => handleStatusToggle(option.value)}
                      className={`flex items-center space-x-3 p-3 rounded-lg border-2 transition-all ${
                        filters.status.includes(option.value)
                          ? 'border-current shadow-md'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      style={{
                        borderColor: filters.status.includes(option.value) ? option.color : undefined,
                        backgroundColor: filters.status.includes(option.value)
                          ? `${option.color}15`
                          : undefined,
                      }}
                    >
                      <span className="text-2xl">{option.emoji}</span>
                      <span
                        className={`text-sm font-medium ${
                          filters.status.includes(option.value) ? 'text-gray-900' : 'text-gray-600'
                        }`}
                      >
                        {option.label}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Probability Range */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Probabilidad de Contratación
                </label>
                <div className="space-y-3">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-gray-600">Mínimo</span>
                      <span className="text-sm font-bold text-indigo-600">
                        {filters.minProbability}%
                      </span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={filters.minProbability}
                      onChange={(e) =>
                        onFiltersChange({ ...filters, minProbability: parseInt(e.target.value) })
                      }
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                    />
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-gray-600">Máximo</span>
                      <span className="text-sm font-bold text-indigo-600">
                        {filters.maxProbability}%
                      </span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={filters.maxProbability}
                      onChange={(e) =>
                        onFiltersChange({ ...filters, maxProbability: parseInt(e.target.value) })
                      }
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                    />
                  </div>
                </div>
              </div>

              {/* Region Filter */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Regiones
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {regionOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => handleRegionToggle(option.value)}
                      className={`px-3 py-2 text-sm rounded-lg border-2 transition-all ${
                        filters.regions.includes(option.value)
                          ? 'bg-indigo-50 border-indigo-500 text-indigo-700 font-semibold'
                          : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Funding Stage Filter */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Etapa de Funding
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {fundingStageOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => handleFundingStageToggle(option.value)}
                      className={`px-3 py-2 text-xs rounded-lg border-2 transition-all ${
                        filters.fundingStages.includes(option.value)
                          ? 'bg-purple-50 border-purple-500 text-purple-700 font-semibold'
                          : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300'
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Funding Amount Range */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Funding Total (USD)
                </label>
                <div className="space-y-3">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-gray-600">Mínimo</span>
                      <span className="text-sm font-bold text-green-600">
                        ${(filters.minFunding / 1000000).toFixed(1)}M
                      </span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100000000"
                      step="1000000"
                      value={filters.minFunding}
                      onChange={(e) =>
                        onFiltersChange({ ...filters, minFunding: parseInt(e.target.value) })
                      }
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-green-600"
                    />
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-gray-600">Máximo</span>
                      <span className="text-sm font-bold text-green-600">
                        ${(filters.maxFunding / 1000000).toFixed(1)}M
                      </span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100000000"
                      step="1000000"
                      value={filters.maxFunding}
                      onChange={(e) =>
                        onFiltersChange({ ...filters, maxFunding: parseInt(e.target.value) })
                      }
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-green-600"
                    />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
