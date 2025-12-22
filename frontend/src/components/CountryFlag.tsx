'use client';

import React from 'react';
import { COUNTRY_FLAGS } from '@/lib/americasMapData';

interface CountryFlagProps {
  countryCode: string;
  countryName?: string;
  size?: 'sm' | 'md' | 'lg';
  showTooltip?: boolean;
  className?: string;
}

export default function CountryFlag({ 
  countryCode, 
  countryName,
  size = 'md',
  showTooltip = true,
  className = ''
}: CountryFlagProps) {
  const flag = COUNTRY_FLAGS[countryCode] || '🌎';
  
  const sizeClasses = {
    sm: 'text-base',
    md: 'text-xl',
    lg: 'text-3xl'
  };

  return (
    <span 
      className={`inline-flex items-center ${sizeClasses[size]} ${className}`}
      title={showTooltip && countryName ? countryName : undefined}
      role="img"
      aria-label={countryName || countryCode}
    >
      {flag}
    </span>
  );
}

// Convenience component for flag with country name
export function CountryFlagWithName({ 
  countryCode, 
  countryName,
  layout = 'horizontal'
}: { 
  countryCode: string; 
  countryName: string;
  layout?: 'horizontal' | 'vertical';
}) {
  const flag = COUNTRY_FLAGS[countryCode] || '🌎';

  if (layout === 'vertical') {
    return (
      <div className="flex flex-col items-center gap-1">
        <span className="text-2xl">{flag}</span>
        <span className="text-xs text-gray-400 text-center">{countryName}</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-xl">{flag}</span>
      <span className="text-sm font-medium text-gray-300">{countryName}</span>
    </div>
  );
}

// Badge component for country code
export function CountryBadge({ 
  countryCode, 
  countryName,
  variant = 'default'
}: { 
  countryCode: string; 
  countryName?: string;
  variant?: 'default' | 'compact';
}) {
  const flag = COUNTRY_FLAGS[countryCode] || '🌎';

  if (variant === 'compact') {
    return (
      <span 
        className="inline-flex items-center gap-1 px-2 py-1 bg-gray-800 border border-gray-700 rounded text-xs"
        title={countryName}
      >
        <span>{flag}</span>
        <span className="font-mono text-gray-400">{countryCode}</span>
      </span>
    );
  }

  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-800/50 border border-gray-700 rounded-lg">
      <span className="text-lg">{flag}</span>
      <div className="flex flex-col">
        <span className="text-xs font-mono text-gray-500">{countryCode}</span>
        {countryName && (
          <span className="text-xs font-medium text-gray-300">{countryName}</span>
        )}
      </div>
    </div>
  );
}
