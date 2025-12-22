'use client';

import React from 'react';

/**
 * UnlockButton Component
 * 
 * Redirects to Stripe Payment Link (no backend API call)
 * Triggers FOMO with premium styling
 * 
 * Props:
 *   - variant: Button size/style ('mini' | 'default' | 'large')
 *   - columnType: For analytics tracking (optional)
 * 
 * Setup:
 *   1. Create Payment Link in Stripe Dashboard
 *   2. Add NEXT_PUBLIC_STRIPE_PAYMENT_LINK to .env.local
 *   3. Configure success_url to /success
 * 
 * Usage:
 *   <UnlockButton variant="large" />
 *   <UnlockButton variant="mini" columnType="email" />
 */

interface UnlockButtonProps {
  variant?: 'mini' | 'default' | 'large';
  columnType?: 'email' | 'phone' | 'funding';
  className?: string;
}

export function UnlockButton({ 
  variant = 'default',
  columnType,
  className = ''
}: UnlockButtonProps) {
  const stripePaymentLink = process.env.NEXT_PUBLIC_STRIPE_PAYMENT_LINK || '#';

  const handleClick = () => {
    // Analytics tracking (optional)
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'unlock_button_click', {
        button_variant: variant,
        column_type: columnType || 'general',
      });
    }

    // Redirect to Stripe Payment Link
    window.location.href = stripePaymentLink;
  };

  // Mini variant (for inline column overlays)
  if (variant === 'mini') {
    return (
      <button
        onClick={handleClick}
        className={`
          px-3 py-1 
          bg-gradient-to-r from-blue-600 to-purple-600 
          text-white text-xs font-semibold 
          rounded-full 
          shadow-lg
          hover:shadow-xl hover:scale-105 
          transform transition-all duration-200
          whitespace-nowrap
          ${className}
        `}
      >
        🔓 Unlock
      </button>
    );
  }

  // Large variant (for section overlays)
  if (variant === 'large') {
    return (
      <button
        onClick={handleClick}
        className={`
          group relative
          px-8 py-4 
          bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 
          text-white text-lg font-bold 
          rounded-xl 
          shadow-2xl
          hover:shadow-3xl hover:scale-105 
          transform transition-all duration-300
          overflow-hidden
          ${className}
        `}
      >
        {/* Animated gradient background */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        
        {/* Button content */}
        <span className="relative z-10 flex items-center space-x-3">
          <svg 
            className="w-6 h-6" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" 
            />
          </svg>
          <span>Unlock Global Leads</span>
          <svg 
            className="w-5 h-5 group-hover:translate-x-1 transition-transform" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M13 7l5 5m0 0l-5 5m5-5H6" 
            />
          </svg>
        </span>

        {/* Shimmer effect */}
        <div className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
      </button>
    );
  }

  // Default variant (for row/table overlays)
  return (
    <button
      onClick={handleClick}
      className={`
        px-6 py-3 
        bg-gradient-to-r from-blue-600 to-purple-600 
        text-white font-semibold 
        rounded-lg 
        shadow-lg
        hover:shadow-xl hover:scale-105 
        transform transition-all duration-200
        flex items-center space-x-2
        ${className}
      `}
    >
      <svg 
        className="w-5 h-5" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" 
        />
      </svg>
      <span>Unlock Global Leads</span>
    </button>
  );
}

/**
 * PricingBadge Component
 * 
 * Shows pricing near unlock button for added context
 */

interface PricingBadgeProps {
  price?: string;
  period?: string;
  className?: string;
}

export function PricingBadge({ 
  price = '$49',
  period = 'month',
  className = ''
}: PricingBadgeProps) {
  return (
    <div className={`inline-flex items-baseline space-x-1 ${className}`}>
      <span className="text-3xl font-bold text-gray-900">{price}</span>
      <span className="text-sm text-gray-500">/{period}</span>
    </div>
  );
}

/**
 * FeatureBadge Component
 * 
 * Highlight key feature to trigger FOMO
 */

interface FeatureBadgeProps {
  text: string;
  icon?: React.ReactNode;
  className?: string;
}

export function FeatureBadge({ 
  text,
  icon,
  className = ''
}: FeatureBadgeProps) {
  return (
    <div className={`
      inline-flex items-center space-x-2 
      px-4 py-2 
      bg-blue-50 
      border border-blue-200 
      rounded-full 
      ${className}
    `}>
      {icon || (
        <svg 
          className="w-4 h-4 text-blue-600" 
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
      )}
      <span className="text-sm font-medium text-blue-900">{text}</span>
    </div>
  );
}
