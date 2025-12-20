/**
 * Utility functions
 */

import { type ClassValue, clsx } from 'clsx';
import { TrafficLightStatus, Company } from '@/types';

// Tailwind class merger
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

/**
 * Determine traffic light status based on company metrics
 */
export function getTrafficLightStatus(company: {
  hiring_probability: number;
  funding_recency: number;
  tech_churn: number;
  job_post_velocity: number;
  senior_departures: number;
}): { status: TrafficLightStatus; reason: string } {
  const {
    hiring_probability,
    funding_recency,
    tech_churn,
    job_post_velocity,
    senior_departures,
  } = company;

  // 🔴 RED: Riesgo de cierre/despidos
  if (
    tech_churn > 20 ||
    (senior_departures >= 5 && job_post_velocity < 0.5) ||
    (funding_recency > 730 && hiring_probability < 20)
  ) {
    return {
      status: 'red',
      reason: tech_churn > 20
        ? `Alto churn (${tech_churn.toFixed(1)}%) indica problemas internos`
        : senior_departures >= 5
        ? `${senior_departures} seniors salieron + baja actividad de hiring`
        : 'Sin funding >2 años + baja probabilidad de contratación',
    };
  }

  // 🟡 GOLDEN: Ronda de financiamiento inminente
  if (
    funding_recency < 90 &&
    hiring_probability >= 70 &&
    job_post_velocity > 2.0
  ) {
    return {
      status: 'golden',
      reason: `Funding hace ${funding_recency} días + ${hiring_probability.toFixed(0)}% probabilidad + surge ${job_post_velocity.toFixed(1)}x`,
    };
  }

  // 🟢 GREEN: Alta probabilidad de contratación
  if (hiring_probability >= 70 || (hiring_probability >= 60 && job_post_velocity > 1.5)) {
    return {
      status: 'green',
      reason: `${hiring_probability.toFixed(0)}% probabilidad de contratación + velocity ${job_post_velocity.toFixed(1)}x`,
    };
  }

  // 🔵 BLUE: Estable (default)
  return {
    status: 'blue',
    reason: `Empresa estable con ${hiring_probability.toFixed(0)}% probabilidad de contratación`,
  };
}

/**
 * Format currency
 */
export function formatCurrency(amount: number, decimals: number = 1): string {
  if (amount >= 1000) {
    return `$${(amount / 1000).toFixed(decimals)}B`;
  }
  return `$${amount.toFixed(decimals)}M`;
}

/**
 * Format percentage
 */
export function formatPercentage(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Format date relative to now
 */
export function formatRelativeDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Hoy';
  if (diffDays === 1) return 'Ayer';
  if (diffDays < 7) return `Hace ${diffDays} días`;
  if (diffDays < 30) return `Hace ${Math.floor(diffDays / 7)} semanas`;
  if (diffDays < 365) return `Hace ${Math.floor(diffDays / 30)} meses`;
  return `Hace ${Math.floor(diffDays / 365)} años`;
}

/**
 * Get color for traffic light status
 */
export function getStatusColor(status: TrafficLightStatus): string {
  const colors: Record<TrafficLightStatus, string> = {
    red: '#EF4444',
    green: '#10B981',
    golden: '#F59E0B',
    blue: '#3B82F6',
  };
  return colors[status];
}

/**
 * Get status label
 */
export function getStatusLabel(status: TrafficLightStatus): string {
  const labels: Record<TrafficLightStatus, string> = {
    red: 'Alto Riesgo',
    green: 'Alta Contratación',
    golden: 'Funding Inminente',
    blue: 'Estable',
  };
  return labels[status];
}

/**
 * Get status emoji
 */
export function getStatusEmoji(status: TrafficLightStatus): string {
  const emojis: Record<TrafficLightStatus, string> = {
    red: '🔴',
    green: '🟢',
    golden: '🟡',
    blue: '🔵',
  };
  return emojis[status];
}

/**
 * Get confidence badge color
 */
export function getConfidenceBadgeColor(confidence: string): string {
  switch (confidence.toLowerCase()) {
    case 'very high':
      return 'bg-green-100 text-green-800 border-green-200';
    case 'high':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'low':
      return 'bg-gray-100 text-gray-800 border-gray-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
}

/**
 * Sort companies by priority
 */
export function sortCompaniesByPriority(companies: Company[]): Company[] {
  const priorityOrder: Record<TrafficLightStatus, number> = {
    golden: 1,
    green: 2,
    red: 3,
    blue: 4,
  };

  return [...companies].sort((a, b) => {
    const priorityDiff = priorityOrder[a.status] - priorityOrder[b.status];
    if (priorityDiff !== 0) return priorityDiff;

    // Within same status, sort by probability
    return b.hiring_probability - a.hiring_probability;
  });
}

/**
 * Generate mock coordinates for cities (placeholder)
 */
export function getCityCoordinates(city: string, country: string): { lat: number; lng: number } {
  // Mock data - In production, use a geocoding API
  const coordinates: Record<string, { lat: number; lng: number }> = {
    'san francisco_usa': { lat: 37.7749, lng: -122.4194 },
    'new york_usa': { lat: 40.7128, lng: -74.0060 },
    'london_uk': { lat: 51.5074, lng: -0.1278 },
    'berlin_germany': { lat: 52.5200, lng: 13.4050 },
    'sao paulo_brazil': { lat: -23.5505, lng: -46.6333 },
    'buenos aires_argentina': { lat: -34.6037, lng: -58.3816 },
    'tokyo_japan': { lat: 35.6762, lng: 139.6503 },
    'singapore_singapore': { lat: 1.3521, lng: 103.8198 },
  };

  const key = `${city.toLowerCase()}_${country.toLowerCase()}`;
  return coordinates[key] || { lat: 0, lng: 0 };
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}
