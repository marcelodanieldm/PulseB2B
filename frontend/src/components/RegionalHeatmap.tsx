'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  AMERICAS_COUNTRIES, 
  REGION_COLORS, 
  getCountriesByRegion,
  type CountryData 
} from '@/lib/americasMapData';

interface RegionalHeatmapProps {
  data?: Record<string, {
    leadCount: number;
    avgPulseScore: number;
    criticalLeads: number;
    arbitrageScore?: number;
  }>;
  selectedRegion?: string;
  onCountryClick?: (countryCode: string) => void;
}

export default function RegionalHeatmap({ 
  data = {}, 
  selectedRegion = 'all',
  onCountryClick 
}: RegionalHeatmapProps) {
  const [hoveredCountry, setHoveredCountry] = useState<CountryData | null>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Calculate heat intensity (0-1) based on lead count
  const getHeatIntensity = (countryCode: string): number => {
    const countryData = data[countryCode];
    if (!countryData) return 0;
    
    const maxLeads = Math.max(...Object.values(data).map(d => d.leadCount), 1);
    return countryData.leadCount / maxLeads;
  };

  // Get color based on heat intensity
  const getCountryColor = (country: CountryData): string => {
    const intensity = getHeatIntensity(country.code);
    const baseColor = REGION_COLORS[country.region];
    
    if (intensity === 0) return '#1F2937'; // Dark gray for no data
    
    // Gradient from base color to bright based on intensity
    const opacity = 0.3 + (intensity * 0.7); // 30% to 100% opacity
    return baseColor + Math.round(opacity * 255).toString(16).padStart(2, '0');
  };

  // Filter countries by selected region
  const displayedCountries = selectedRegion === 'all' 
    ? AMERICAS_COUNTRIES 
    : getCountriesByRegion(selectedRegion);

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    const svg = e.currentTarget;
    const rect = svg.getBoundingClientRect();
    setMousePosition({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
  };

  return (
    <div className="relative w-full h-full">
      {/* SVG Map */}
      <svg
        viewBox="0 0 800 1650"
        className="w-full h-full"
        onMouseMove={handleMouseMove}
        style={{ minHeight: '600px' }}
      >
        {/* Background */}
        <rect width="800" height="1650" fill="#0F172A" />
        
        {/* Country paths */}
        {displayedCountries.map((country) => {
          const countryData = data[country.code];
          const isActive = countryData && countryData.leadCount > 0;
          
          return (
            <motion.g key={country.code}>
              {/* Country shape */}
              <motion.path
                d={country.path}
                fill={getCountryColor(country)}
                stroke={hoveredCountry?.code === country.code ? '#FFFFFF' : '#374151'}
                strokeWidth={hoveredCountry?.code === country.code ? 3 : 1}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ 
                  opacity: 1, 
                  scale: 1,
                  fill: getCountryColor(country)
                }}
                transition={{ duration: 0.5, delay: displayedCountries.indexOf(country) * 0.05 }}
                whileHover={{ 
                  scale: 1.05,
                  transition: { duration: 0.2 }
                }}
                onMouseEnter={() => setHoveredCountry(country)}
                onMouseLeave={() => setHoveredCountry(null)}
                onClick={() => onCountryClick?.(country.code)}
                className={`cursor-pointer ${isActive ? 'drop-shadow-lg' : ''}`}
                style={{
                  filter: hoveredCountry?.code === country.code 
                    ? 'brightness(1.3) drop-shadow(0 0 10px rgba(255,255,255,0.5))' 
                    : 'none'
                }}
              />
              
              {/* Pulse animation for active countries */}
              {isActive && countryData.criticalLeads > 0 && (
                <motion.circle
                  cx={country.centroid[0]}
                  cy={country.centroid[1]}
                  r={8}
                  fill="#EF4444"
                  initial={{ opacity: 0.8, scale: 1 }}
                  animate={{ 
                    opacity: [0.8, 0.3, 0.8],
                    scale: [1, 1.5, 1]
                  }}
                  transition={{ 
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                />
              )}
              
              {/* Country label */}
              <text
                x={country.centroid[0]}
                y={country.centroid[1]}
                fontSize="12"
                fontWeight="bold"
                fill={isActive ? '#FFFFFF' : '#6B7280'}
                textAnchor="middle"
                dominantBaseline="middle"
                pointerEvents="none"
                className="select-none"
              >
                {country.code}
              </text>
            </motion.g>
          );
        })}
        
        {/* Region labels */}
        <text x="350" y="30" fontSize="16" fontWeight="bold" fill="#3B82F6" textAnchor="middle">
          NORTH AMERICA
        </text>
        <text x="320" y="450" fontSize="16" fontWeight="bold" fill="#10B981" textAnchor="middle">
          CENTRAL
        </text>
        <text x="430" y="750" fontSize="16" fontWeight="bold" fill="#F59E0B" textAnchor="middle">
          ANDEAN
        </text>
        <text x="520" y="1420" fontSize="16" fontWeight="bold" fill="#EF4444" textAnchor="middle">
          SOUTHERN CONE
        </text>
      </svg>

      {/* Hover tooltip */}
      {hoveredCountry && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0 }}
          className="absolute z-50 bg-gray-900 border border-gray-700 rounded-lg p-4 shadow-2xl pointer-events-none"
          style={{
            left: mousePosition.x + 20,
            top: mousePosition.y + 20,
            minWidth: '240px'
          }}
        >
          {/* Country header */}
          <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-700">
            <span className="text-3xl">{hoveredCountry.code === 'CA' ? '🇨🇦' : 
                                        hoveredCountry.code === 'US' ? '🇺🇸' :
                                        hoveredCountry.code === 'MX' ? '🇲🇽' :
                                        hoveredCountry.code === 'GT' ? '🇬🇹' :
                                        hoveredCountry.code === 'CR' ? '🇨🇷' :
                                        hoveredCountry.code === 'PA' ? '🇵🇦' :
                                        hoveredCountry.code === 'CO' ? '🇨🇴' :
                                        hoveredCountry.code === 'VE' ? '🇻🇪' :
                                        hoveredCountry.code === 'EC' ? '🇪🇨' :
                                        hoveredCountry.code === 'PE' ? '🇵🇪' :
                                        hoveredCountry.code === 'BO' ? '🇧🇴' :
                                        hoveredCountry.code === 'BR' ? '🇧🇷' :
                                        hoveredCountry.code === 'PY' ? '🇵🇾' :
                                        hoveredCountry.code === 'CL' ? '🇨🇱' :
                                        hoveredCountry.code === 'AR' ? '🇦🇷' :
                                        hoveredCountry.code === 'UY' ? '🇺🇾' : '🌎'}</span>
            <div>
              <h3 className="font-bold text-white text-lg">{hoveredCountry.name}</h3>
              <p className="text-xs text-gray-400">{hoveredCountry.currency} | UTC{hoveredCountry.timezone >= 0 ? '+' : ''}{hoveredCountry.timezone}</p>
            </div>
          </div>

          {/* Stats */}
          {data[hoveredCountry.code] ? (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Total Leads:</span>
                <span className="font-bold text-white text-lg">{data[hoveredCountry.code].leadCount}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Avg Pulse Score:</span>
                <span className="font-semibold text-blue-400">{data[hoveredCountry.code].avgPulseScore.toFixed(0)}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">🔥 Critical Leads:</span>
                <span className="font-bold text-red-400">{data[hoveredCountry.code].criticalLeads}</span>
              </div>
              
              {data[hoveredCountry.code].arbitrageScore && (
                <div className="mt-3 pt-2 border-t border-gray-700">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400">💰 Arbitrage Score:</span>
                    <span className="font-bold text-green-400">{data[hoveredCountry.code].arbitrageScore?.toFixed(0)}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Cost-benefit opportunity</p>
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No data available</p>
          )}
        </motion.div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-gray-900/90 backdrop-blur-sm border border-gray-700 rounded-lg p-4">
        <h4 className="text-xs font-bold text-gray-400 mb-2">HEAT INTENSITY</h4>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: '#EF4444' }}></div>
            <span className="text-xs text-gray-300">High Activity</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: '#F59E0B80' }}></div>
            <span className="text-xs text-gray-300">Medium Activity</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-gray-700"></div>
            <span className="text-xs text-gray-300">No Data</span>
          </div>
        </div>
        
        <div className="mt-3 pt-3 border-t border-gray-700">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
            <span className="text-xs text-gray-300">Critical Signals</span>
          </div>
        </div>
      </div>
    </div>
  );
}
