'use client';

import React from 'react';
import { usePremiumStatus } from '@/hooks/usePremiumStatus';
import { UnlockButton } from './UnlockButton';

/**
 * GatedColumn Component
 * 
 * Displays content with blur effect for non-premium users
 * Shows "Unlock Global Leads" button overlay
 * 
 * Props:
 *   - value: The actual content to display/blur
 *   - columnType: Type of column for analytics ('email' | 'phone' | 'funding')
 *   - showButton: Whether to show unlock button (default: true)
 * 
 * Usage:
 *   <GatedColumn value="john@acme.com" columnType="email" />
 *   <GatedColumn value="+1-555-0123" columnType="phone" />
 *   <GatedColumn value="$5,000,000" columnType="funding" />
 */

interface GatedColumnProps {
  value: string | number | null | undefined;
  columnType: 'email' | 'phone' | 'funding';
  showButton?: boolean;
  className?: string;
}

export function GatedColumn({ 
  value, 
  columnType, 
  showButton = true,
  className = '' 
}: GatedColumnProps) {
  const { isPremium, loading } = usePremiumStatus();

  // Show loading skeleton
  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-24"></div>
      </div>
    );
  }

  // Premium users see actual content
  if (isPremium) {
    return (
      <div className={`font-medium text-gray-900 ${className}`}>
        {value || '—'}
      </div>
    );
  }

  // Non-premium users see blurred content with unlock button
  return (
    <div className="relative group">
      {/* Blurred Content (FOMO Effect) */}
      <div 
        className={`
          blur-md 
          select-none 
          pointer-events-none 
          text-gray-400
          ${className}
        `}
        aria-hidden="true"
      >
        {getPlaceholderText(columnType)}
      </div>

      {/* Unlock Button Overlay */}
      {showButton && (
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <UnlockButton 
            columnType={columnType}
            variant="mini"
          />
        </div>
      )}

      {/* Accessibility: Screen reader text */}
      <span className="sr-only">
        Premium content - Sign up to view {columnType}
      </span>
    </div>
  );
}

/**
 * Get placeholder text that looks realistic when blurred
 */
function getPlaceholderText(columnType: 'email' | 'phone' | 'funding'): string {
  switch (columnType) {
    case 'email':
      return 'contact@company.com';
    case 'phone':
      return '+1 (555) 123-4567';
    case 'funding':
      return '$5,000,000';
    default:
      return '•••••••••';
  }
}

/**
 * GatedRow Component
 * 
 * Wrapper for entire row with gated columns
 * Shows single unlock button for the entire row
 */

interface GatedRowProps {
  children: React.ReactNode;
  showUnlockButton?: boolean;
}

export function GatedRow({ children, showUnlockButton = true }: GatedRowProps) {
  const { isPremium, loading } = usePremiumStatus();

  if (loading) {
    return <>{children}</>;
  }

  if (isPremium) {
    return <>{children}</>;
  }

  return (
    <div className="relative group">
      {/* Blurred Row Content */}
      <div className="blur-sm select-none pointer-events-none">
        {children}
      </div>

      {/* Unlock Button Overlay */}
      {showUnlockButton && (
        <div className="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <UnlockButton variant="default" />
        </div>
      )}
    </div>
  );
}

/**
 * GatedSection Component
 * 
 * Wrapper for entire section/table with premium content
 * Shows large unlock overlay
 */

interface GatedSectionProps {
  children: React.ReactNode;
  title?: string;
  description?: string;
}

export function GatedSection({ 
  children, 
  title = 'Premium Data',
  description = 'Unlock to access complete lead information'
}: GatedSectionProps) {
  const { isPremium, loading } = usePremiumStatus();

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded w-48"></div>
        <div className="h-64 bg-gray-100 rounded"></div>
      </div>
    );
  }

  if (isPremium) {
    return <>{children}</>;
  }

  return (
    <div className="relative">
      {/* Blurred Content */}
      <div className="blur-md select-none pointer-events-none opacity-50">
        {children}
      </div>

      {/* Premium Overlay */}
      <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-b from-white/95 to-white/98 backdrop-blur-sm">
        <div className="text-center space-y-6 max-w-md px-8">
          {/* Lock Icon */}
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <svg 
              className="w-8 h-8 text-white" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" 
              />
            </svg>
          </div>

          {/* Title */}
          <div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              {title}
            </h3>
            <p className="text-gray-600">
              {description}
            </p>
          </div>

          {/* Features List */}
          <div className="text-left space-y-2">
            <Feature text="Direct email contacts for every lead" />
            <Feature text="Phone numbers for immediate outreach" />
            <Feature text="Exact funding amounts and dates" />
            <Feature text="Unlimited data exports (CSV, JSON)" />
          </div>

          {/* Unlock Button */}
          <UnlockButton variant="large" />

          {/* Trust Badge */}
          <p className="text-sm text-gray-500">
            ✓ Cancel anytime · ✓ 7-day money-back guarantee
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * Feature Component
 * Small checkmark feature for premium overlay
 */
function Feature({ text }: { text: string }) {
  return (
    <div className="flex items-center space-x-2">
      <svg 
        className="w-5 h-5 text-green-500 flex-shrink-0" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M5 13l4 4L19 7" 
        />
      </svg>
      <span className="text-sm text-gray-700">{text}</span>
    </div>
  );
}
