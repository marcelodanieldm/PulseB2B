/**
 * Global Opportunities Map Component
 * Interactive map with Mapbox showing companies with traffic light system
 */

'use client';

import { useState, useCallback, useMemo } from 'react';
import Map, { Marker, Popup, NavigationControl, ScaleControl } from 'react-map-gl';
import { MapPin, TrendingUp, DollarSign, Users, Calendar } from 'lucide-react';
import 'mapbox-gl/dist/mapbox-gl.css';

import { Company, MapFilters } from '@/types';
import { getStatusColor, getStatusEmoji, formatCurrency, formatRelativeDate } from '@/lib/utils';

interface OpportunitiesMapProps {
  companies: Company[];
  filters: MapFilters;
  selectedCompany: Company | null;
  onCompanySelect: (company: Company | null) => void;
}

export default function OpportunitiesMap({
  companies,
  filters,
  selectedCompany,
  onCompanySelect,
}: OpportunitiesMapProps) {
  const [viewState, setViewState] = useState({
    longitude: -40,
    latitude: 20,
    zoom: 2,
  });

  const [popupInfo, setPopupInfo] = useState<Company | null>(null);

  // Filter companies based on filters
  const filteredCompanies = useMemo(() => {
    return companies.filter((company) => {
      // Status filter
      if (filters.status.length > 0 && !filters.status.includes(company.status)) {
        return false;
      }

      // Probability range
      if (
        company.hiring_probability < filters.minProbability ||
        company.hiring_probability > filters.maxProbability
      ) {
        return false;
      }

      // Region filter
      if (filters.regions.length > 0 && !filters.regions.includes(company.region)) {
        return false;
      }

      // Funding stage filter
      if (
        filters.fundingStages.length > 0 &&
        !filters.fundingStages.includes(company.funding_stage)
      ) {
        return false;
      }

      // Funding amount range
      if (
        company.total_funding < filters.minFunding ||
        company.total_funding > filters.maxFunding
      ) {
        return false;
      }

      return true;
    });
  }, [companies, filters]);

  // Handle marker click
  const handleMarkerClick = useCallback(
    (company: Company) => {
      setPopupInfo(company);
      onCompanySelect(company);
    },
    [onCompanySelect]
  );

  // Get marker size based on probability
  const getMarkerSize = (probability: number): number => {
    if (probability >= 80) return 48;
    if (probability >= 60) return 40;
    if (probability >= 40) return 32;
    return 24;
  };

  return (
    <div className="relative h-full w-full rounded-xl overflow-hidden shadow-2xl">
      <Map
        {...viewState}
        onMove={(evt) => setViewState(evt.viewState)}
        mapStyle="mapbox://styles/mapbox/dark-v11"
        mapboxAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}
        style={{ width: '100%', height: '100%' }}
        attributionControl={false}
      >
        {/* Map Controls */}
        <NavigationControl position="top-right" />
        <ScaleControl position="bottom-right" />

        {/* Company Markers */}
        {filteredCompanies.map((company) => {
          const size = getMarkerSize(company.hiring_probability);
          const color = getStatusColor(company.status);

          return (
            <Marker
              key={company.id}
              longitude={company.longitude}
              latitude={company.latitude}
              anchor="bottom"
              onClick={(e) => {
                e.originalEvent.stopPropagation();
                handleMarkerClick(company);
              }}
            >
              <div
                className="relative cursor-pointer transition-all hover:scale-110"
                style={{ width: size, height: size }}
              >
                {/* Pulse animation for high priority */}
                {company.status === 'golden' && (
                  <div
                    className="absolute inset-0 rounded-full animate-ping opacity-75"
                    style={{ backgroundColor: color }}
                  />
                )}

                {/* Main marker */}
                <div
                  className="relative w-full h-full rounded-full border-4 border-white shadow-lg flex items-center justify-center"
                  style={{ backgroundColor: color }}
                >
                  <span className="text-white text-xl font-bold">
                    {getStatusEmoji(company.status)}
                  </span>
                </div>

                {/* Probability badge */}
                <div className="absolute -top-2 -right-2 bg-white rounded-full px-2 py-0.5 text-xs font-bold shadow-md border-2"
                     style={{ borderColor: color, color: color }}>
                  {company.hiring_probability.toFixed(0)}%
                </div>
              </div>
            </Marker>
          );
        })}

        {/* Popup */}
        {popupInfo && (
          <Popup
            anchor="top"
            longitude={popupInfo.longitude}
            latitude={popupInfo.latitude}
            onClose={() => setPopupInfo(null)}
            closeButton={true}
            closeOnClick={false}
            className="custom-popup"
          >
            <div className="p-4 min-w-[320px]">
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">
                    {popupInfo.name}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {popupInfo.city}, {popupInfo.country}
                  </p>
                </div>
                <div
                  className="text-3xl"
                  title={popupInfo.status_reason}
                >
                  {getStatusEmoji(popupInfo.status)}
                </div>
              </div>

              {/* Probability */}
              <div className="mb-3 p-3 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">
                    Probabilidad de Contratación
                  </span>
                  <span
                    className="text-2xl font-bold"
                    style={{ color: getStatusColor(popupInfo.status) }}
                  >
                    {popupInfo.hiring_probability.toFixed(1)}%
                  </span>
                </div>
                <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full transition-all duration-500"
                    style={{
                      width: `${popupInfo.hiring_probability}%`,
                      backgroundColor: getStatusColor(popupInfo.status),
                    }}
                  />
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div className="flex items-center space-x-2">
                  <DollarSign className="w-4 h-4 text-green-600" />
                  <div>
                    <p className="text-xs text-gray-500">Funding</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {formatCurrency(popupInfo.total_funding)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Users className="w-4 h-4 text-blue-600" />
                  <div>
                    <p className="text-xs text-gray-500">Team Size</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {popupInfo.team_size}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <TrendingUp className="w-4 h-4 text-purple-600" />
                  <div>
                    <p className="text-xs text-gray-500">Velocity</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {popupInfo.job_post_velocity.toFixed(1)}x
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-orange-600" />
                  <div>
                    <p className="text-xs text-gray-500">Last Funding</p>
                    <p className="text-sm font-semibold text-gray-900">
                      {formatRelativeDate(popupInfo.last_funding_date)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Status Reason */}
              <div className="p-2 bg-gray-50 rounded text-xs text-gray-600 italic">
                {popupInfo.status_reason}
              </div>

              {/* Action Button */}
              <button
                onClick={() => onCompanySelect(popupInfo)}
                className="mt-3 w-full py-2 px-4 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors"
              >
                Ver Detalles Completos →
              </button>
            </div>
          </Popup>
        )}
      </Map>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-xl p-4">
        <h4 className="text-sm font-bold text-gray-900 mb-3">Traffic Light System</h4>
        <div className="space-y-2">
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 rounded-full bg-risk-high flex items-center justify-center">
              <span className="text-white text-sm">🔴</span>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-900">Alto Riesgo</p>
              <p className="text-xs text-gray-500">Cierre/Despidos</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 rounded-full bg-risk-low flex items-center justify-center">
              <span className="text-white text-sm">🟢</span>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-900">Alta Contratación</p>
              <p className="text-xs text-gray-500">≥70% probabilidad</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 rounded-full bg-opportunity-funding flex items-center justify-center animate-pulse-slow">
              <span className="text-white text-sm">🟡</span>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-900">Funding Inminente</p>
              <p className="text-xs text-gray-500">Post-funding <90d</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 rounded-full bg-opportunity-stable flex items-center justify-center">
              <span className="text-white text-sm">🔵</span>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-900">Estable</p>
              <p className="text-xs text-gray-500">Normal</p>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs font-semibold text-gray-700">
            {filteredCompanies.length} empresas visibles
          </p>
        </div>
      </div>

      {/* Cluster Stats (Top Right) */}
      <div className="absolute top-4 left-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-xl p-4">
        <h4 className="text-sm font-bold text-gray-900 mb-2">Distribución Global</h4>
        <div className="grid grid-cols-2 gap-3">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {filteredCompanies.filter(c => c.status === 'green').length}
            </div>
            <div className="text-xs text-gray-600">Alta Prob.</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {filteredCompanies.filter(c => c.status === 'golden').length}
            </div>
            <div className="text-xs text-gray-600">Funding</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {filteredCompanies.filter(c => c.status === 'red').length}
            </div>
            <div className="text-xs text-gray-600">Riesgo</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {filteredCompanies.filter(c => c.status === 'blue').length}
            </div>
            <div className="text-xs text-gray-600">Estable</div>
          </div>
        </div>
      </div>
    </div>
  );
}
