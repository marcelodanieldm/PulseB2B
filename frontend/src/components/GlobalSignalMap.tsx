/**
 * Global Signal Map Component
 * Premium map showing US, Brazil, and Mexico ventures with hiring signals
 */

'use client';

import { useState, useCallback, useMemo } from 'react';
import Map, { Marker, Popup, NavigationControl, ScaleControl, Source, Layer } from 'react-map-gl';
import { TrendingUp, Zap, Target, ExternalLink, Lock } from 'lucide-react';
import 'mapbox-gl/dist/mapbox-gl.css';

import { Company } from '@/types';
import { formatCurrency, formatPercentage } from '@/lib/utils';

interface GlobalSignalMapProps {
  companies: Company[];
  onCompanySelect: (company: Company | null) => void;
  isPremium?: boolean;
  onUnlockClick?: () => void;
}

// Country boundaries for highlighting
const HIGHLIGHTED_COUNTRIES = {
  us: { name: 'United States', center: [-95.7129, 37.0902], zoom: 3.5 },
  brazil: { name: 'Brazil', center: [-47.9292, -15.7801], zoom: 3.5 },
  mexico: { name: 'Mexico', center: [-102.5528, 23.6345], zoom: 4 },
};

export default function GlobalSignalMap({
  companies,
  onCompanySelect,
  isPremium = false,
  onUnlockClick,
}: GlobalSignalMapProps) {
  const [viewState, setViewState] = useState({
    longitude: -70,
    latitude: 15,
    zoom: 2.5,
  });

  const [hoveredCompany, setHoveredCompany] = useState<Company | null>(null);
  const [selectedPopup, setSelectedPopup] = useState<Company | null>(null);

  // Filter companies by target countries
  const targetCompanies = useMemo(() => {
    return companies.filter((company) => {
      const country = company.country.toLowerCase();
      return country === 'usa' || 
             country === 'united states' || 
             country === 'brazil' || 
             country === 'brasil' ||
             country === 'mexico' ||
             country === 'méxico';
    });
  }, [companies]);

  // Get signal strength color
  const getSignalColor = (probability: number): string => {
    if (probability >= 85) return '#10b981'; // Green-500 - Critical
    if (probability >= 70) return '#f59e0b'; // Amber-500 - High
    if (probability >= 50) return '#3b82f6'; // Blue-500 - Medium
    return '#6b7280'; // Gray-500 - Low
  };

  // Get signal glow intensity
  const getSignalGlow = (probability: number): string => {
    if (probability >= 85) return '0 0 20px 10px rgba(16, 185, 129, 0.4)';
    if (probability >= 70) return '0 0 15px 8px rgba(245, 158, 11, 0.3)';
    return '0 0 10px 5px rgba(59, 130, 246, 0.2)';
  };

  // Get marker size based on venture scale
  const getMarkerSize = (company: Company): number => {
    if (company.total_funding >= 100) return 28; // $100M+ = Large
    if (company.total_funding >= 50) return 24;  // $50M-100M = Medium
    if (company.total_funding >= 20) return 20;  // $20M-50M = Small
    return 16; // <$20M = Seed
  };

  // Handle marker click
  const handleMarkerClick = useCallback(
    (company: Company) => {
      if (!isPremium && company.hiring_probability >= 70) {
        // Premium feature locked
        onUnlockClick?.();
        return;
      }
      setSelectedPopup(company);
      onCompanySelect(company);
    },
    [isPremium, onCompanySelect, onUnlockClick]
  );

  // Zoom to country
  const zoomToCountry = (countryKey: keyof typeof HIGHLIGHTED_COUNTRIES) => {
    const country = HIGHLIGHTED_COUNTRIES[countryKey];
    setViewState({
      longitude: country.center[0],
      latitude: country.center[1],
      zoom: country.zoom,
    });
  };

  return (
    <div className="relative h-full w-full rounded-2xl overflow-hidden shadow-2xl border border-gray-200 bg-gradient-to-br from-gray-900 via-blue-900/20 to-purple-900/20">
      {/* Country Quick Nav */}
      <div className="absolute top-6 left-6 z-10 flex gap-2">
        {Object.entries(HIGHLIGHTED_COUNTRIES).map(([key, country]) => (
          <button
            key={key}
            onClick={() => zoomToCountry(key as keyof typeof HIGHLIGHTED_COUNTRIES)}
            className="px-4 py-2 bg-white/90 backdrop-blur-md rounded-lg shadow-lg hover:bg-white transition-all text-sm font-semibold text-gray-900 hover:scale-105"
          >
            {country.name}
          </button>
        ))}
      </div>

      {/* Signal Legend */}
      <div className="absolute top-6 right-6 z-10 bg-white/90 backdrop-blur-md rounded-xl shadow-lg p-4 min-w-[200px]">
        <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-500" />
          Signal Strength
        </h3>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500" style={{ boxShadow: '0 0 10px rgba(16, 185, 129, 0.5)' }}></div>
            <span className="text-xs text-gray-700">Critical (85%+)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-amber-500" style={{ boxShadow: '0 0 8px rgba(245, 158, 11, 0.4)' }}></div>
            <span className="text-xs text-gray-700">High (70-85%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-blue-500"></div>
            <span className="text-xs text-gray-700">Medium (50-70%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-gray-500"></div>
            <span className="text-xs text-gray-700">Low (&lt;50%)</span>
          </div>
        </div>

        {!isPremium && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={onUnlockClick}
              className="w-full px-3 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg text-xs font-semibold hover:from-blue-700 hover:to-purple-700 transition-all flex items-center justify-center gap-2"
            >
              <Lock className="w-3 h-3" />
              Unlock Full Data
            </button>
          </div>
        )}
      </div>

      {/* Stats Summary */}
      <div className="absolute bottom-6 left-6 z-10 bg-white/90 backdrop-blur-md rounded-xl shadow-lg p-4 flex gap-6">
        <div>
          <p className="text-2xl font-bold text-gray-900">{targetCompanies.length}</p>
          <p className="text-xs text-gray-600">Active Ventures</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-green-600">
            {targetCompanies.filter(c => c.hiring_probability >= 85).length}
          </p>
          <p className="text-xs text-gray-600">Critical Signals</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-amber-600">
            {targetCompanies.filter(c => c.hiring_probability >= 70 && c.hiring_probability < 85).length}
          </p>
          <p className="text-xs text-gray-600">High Potential</p>
        </div>
      </div>

      {/* Map */}
      <Map
        {...viewState}
        onMove={(evt) => setViewState(evt.viewState)}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN || 'pk.eyJ1IjoicHVsc2ViMmIiLCJhIjoiY2x2eHh4eHh4eHh4In0.xxxxxxxxxxxxxxxxxxxx'}
        style={{ width: '100%', height: '100%' }}
        maxZoom={12}
        minZoom={1.5}
      >
        {/* Navigation Controls */}
        <NavigationControl position="bottom-right" />
        <ScaleControl position="bottom-left" />

        {/* Company Markers */}
        {targetCompanies.map((company) => {
          const isLocked = !isPremium && company.hiring_probability >= 70;
          const size = getMarkerSize(company);

          return (
            <Marker
              key={company.id}
              longitude={company.longitude}
              latitude={company.latitude}
              anchor="center"
            >
              <div
                className="relative cursor-pointer transition-transform hover:scale-110"
                onClick={() => handleMarkerClick(company)}
                onMouseEnter={() => setHoveredCompany(company)}
                onMouseLeave={() => setHoveredCompany(null)}
              >
                {/* Glow effect for high signals */}
                {company.hiring_probability >= 70 && (
                  <div
                    className="absolute inset-0 rounded-full animate-pulse"
                    style={{
                      boxShadow: getSignalGlow(company.hiring_probability),
                      transform: 'scale(1.5)',
                    }}
                  />
                )}

                {/* Marker */}
                <div
                  className={`relative rounded-full border-2 border-white shadow-lg ${
                    isLocked ? 'opacity-50' : 'opacity-100'
                  }`}
                  style={{
                    width: `${size}px`,
                    height: `${size}px`,
                    backgroundColor: getSignalColor(company.hiring_probability),
                  }}
                >
                  {isLocked && (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Lock className="w-3 h-3 text-white" />
                    </div>
                  )}
                </div>

                {/* Pulse animation for critical signals */}
                {company.hiring_probability >= 85 && !isLocked && (
                  <div
                    className="absolute inset-0 rounded-full border-2 border-green-400 animate-ping"
                    style={{
                      width: `${size}px`,
                      height: `${size}px`,
                    }}
                  />
                )}
              </div>
            </Marker>
          );
        })}

        {/* Hover Tooltip */}
        {hoveredCompany && (
          <Popup
            longitude={hoveredCompany.longitude}
            latitude={hoveredCompany.latitude}
            anchor="top"
            closeButton={false}
            closeOnClick={false}
            className="custom-popup"
            offset={20}
          >
            <div className="p-2 min-w-[200px]">
              <h4 className="font-bold text-sm text-gray-900">{hoveredCompany.name}</h4>
              <p className="text-xs text-gray-600 mt-1">
                {hoveredCompany.city}, {hoveredCompany.country}
              </p>
              <div className="flex items-center gap-2 mt-2">
                <TrendingUp className="w-3 h-3 text-green-600" />
                <span className="text-xs font-semibold text-gray-900">
                  {formatPercentage(hoveredCompany.hiring_probability)} Signal
                </span>
              </div>
            </div>
          </Popup>
        )}

        {/* Selected Company Popup */}
        {selectedPopup && (
          <Popup
            longitude={selectedPopup.longitude}
            latitude={selectedPopup.latitude}
            anchor="left"
            onClose={() => setSelectedPopup(null)}
            className="custom-popup-large"
            maxWidth="400px"
          >
            <div className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-bold text-lg text-gray-900">{selectedPopup.name}</h3>
                  <p className="text-sm text-gray-600">
                    {selectedPopup.city}, {selectedPopup.country}
                  </p>
                </div>
                <div className="text-right">
                  <span
                    className="inline-block px-2 py-1 rounded text-xs font-bold text-white"
                    style={{ backgroundColor: getSignalColor(selectedPopup.hiring_probability) }}
                  >
                    {formatPercentage(selectedPopup.hiring_probability)}
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <p className="text-xs text-gray-500">Runway</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {formatCurrency(selectedPopup.total_funding)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Team Scale</p>
                    <p className="text-sm font-semibold text-gray-900">{selectedPopup.team_size}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Stage</p>
                    <p className="text-sm font-semibold text-gray-900">{selectedPopup.funding_stage}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Scalability</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {selectedPopup.job_post_velocity.toFixed(1)}x
                    </p>
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-500 mb-1">Offshore Potential</p>
                  <div className="flex items-center gap-2">
                    <Target className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-semibold text-gray-900">
                      {selectedPopup.hiring_probability >= 85
                        ? 'Critical - Act Now'
                        : selectedPopup.hiring_probability >= 70
                        ? 'High Priority'
                        : selectedPopup.hiring_probability >= 50
                        ? 'Medium Priority'
                        : 'Monitor'}
                    </span>
                  </div>
                </div>

                {selectedPopup.website && (
                  <a
                    href={selectedPopup.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    <ExternalLink className="w-4 h-4" />
                    Visit Website
                  </a>
                )}
              </div>
            </div>
          </Popup>
        )}
      </Map>
    </div>
  );
}
