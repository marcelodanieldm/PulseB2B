'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { REGION_NAMES, REGION_COLORS } from '@/lib/americasMapData';

interface RegionSelectorProps {
  selectedRegion: string;
  onRegionChange: (region: string) => void;
  stats?: Record<string, { leadCount: number; criticalLeads: number }>;
}

const REGIONS = [
  { id: 'all', name: 'All Regions', icon: '🌎' },
  { id: 'north_america', name: 'North America', icon: '🦅' },
  { id: 'central_america', name: 'Central America', icon: '🌴' },
  { id: 'andean_region', name: 'Andean Region', icon: '⛰️' },
  { id: 'southern_cone', name: 'Southern Cone', icon: '🌊' }
];

export default function RegionSelector({ 
  selectedRegion, 
  onRegionChange,
  stats = {}
}: RegionSelectorProps) {
  return (
    <div className="space-y-3">
      {/* Title */}
      <div className="flex items-center gap-2 mb-4">
        <div className="w-1 h-6 bg-blue-500 rounded-full"></div>
        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider">
          Regional Filter
        </h3>
      </div>

      {/* Region buttons */}
      <div className="grid grid-cols-1 gap-2">
        {REGIONS.map((region) => {
          const isSelected = selectedRegion === region.id;
          const regionStats = stats[region.id];
          const color = region.id === 'all' 
            ? '#6B7280' 
            : REGION_COLORS[region.id as keyof typeof REGION_COLORS];

          return (
            <motion.button
              key={region.id}
              onClick={() => onRegionChange(region.id)}
              whileHover={{ scale: 1.02, x: 4 }}
              whileTap={{ scale: 0.98 }}
              className={`
                relative overflow-hidden rounded-lg p-4 text-left transition-all
                ${isSelected 
                  ? 'bg-gray-800 border-2 shadow-lg' 
                  : 'bg-gray-900 border border-gray-700 hover:border-gray-600'
                }
              `}
              style={{
                borderColor: isSelected ? color : undefined
              }}
            >
              {/* Background gradient effect */}
              {isSelected && (
                <motion.div
                  className="absolute inset-0 opacity-10"
                  style={{ backgroundColor: color }}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 0.1 }}
                  transition={{ duration: 0.3 }}
                />
              )}

              {/* Content */}
              <div className="relative z-10 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {/* Icon */}
                  <span className="text-2xl">{region.icon}</span>
                  
                  {/* Name */}
                  <div>
                    <h4 className={`font-semibold ${isSelected ? 'text-white' : 'text-gray-300'}`}>
                      {region.name}
                    </h4>
                    {regionStats && (
                      <p className="text-xs text-gray-500 mt-0.5">
                        {regionStats.leadCount} leads
                        {regionStats.criticalLeads > 0 && (
                          <span className="text-red-400 ml-2">
                            🔥 {regionStats.criticalLeads} critical
                          </span>
                        )}
                      </p>
                    )}
                  </div>
                </div>

                {/* Selected indicator */}
                {isSelected && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: color }}
                  />
                )}
              </div>

              {/* Active pulse effect */}
              {isSelected && regionStats && regionStats.criticalLeads > 0 && (
                <motion.div
                  className="absolute top-2 right-2 w-2 h-2 rounded-full bg-red-500"
                  animate={{
                    scale: [1, 1.5, 1],
                    opacity: [1, 0.5, 1]
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                />
              )}
            </motion.button>
          );
        })}
      </div>

      {/* Summary stats */}
      {stats['all'] && (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-4 bg-gray-900 border border-gray-800 rounded-lg"
        >
          <h4 className="text-xs font-bold text-gray-500 uppercase mb-3">Global Summary</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-2xl font-bold text-white">{stats['all'].leadCount}</p>
              <p className="text-xs text-gray-500">Total Leads</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-red-400">{stats['all'].criticalLeads}</p>
              <p className="text-xs text-gray-500">Critical</p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
