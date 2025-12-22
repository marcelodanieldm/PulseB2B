/**
 * =====================================================
 * TELEGRAM REFERRAL HOOK
 * =====================================================
 * Purpose: Detect and handle traffic from Telegram bot
 * Author: Senior Frontend Developer
 * Date: December 22, 2025
 * =====================================================
 * 
 * Detects UTM parameters from Telegram bot:
 * - utm_source=telegram
 * - utm_medium=bot
 * - utm_campaign=daily_signal | latest_command
 * 
 * Also supports legacy: source=tg_bot
 * =====================================================
 */

'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';

export interface TelegramReferral {
  isTelegramUser: boolean;
  campaign?: 'daily_signal' | 'latest_command' | 'unknown';
  leadId?: string;
  hasShownWelcome: boolean;
}

/**
 * Hook to detect and track Telegram bot referrals
 */
export function useTelegramReferral() {
  const searchParams = useSearchParams();
  const [referral, setReferral] = useState<TelegramReferral>({
    isTelegramUser: false,
    hasShownWelcome: false,
  });

  useEffect(() => {
    // Check for Telegram UTM parameters
    const utmSource = searchParams?.get('utm_source');
    const utmMedium = searchParams?.get('utm_medium');
    const utmCampaign = searchParams?.get('utm_campaign');
    const legacySource = searchParams?.get('source');
    const leadId = searchParams?.get('lead_id');

    // Detect Telegram referral
    const isTelegramUser =
      (utmSource === 'telegram' && utmMedium === 'bot') ||
      legacySource === 'tg_bot';

    if (isTelegramUser) {
      // Check if we've already shown welcome toast (session storage)
      const hasShownWelcome = sessionStorage.getItem('telegram_welcome_shown') === 'true';

      const campaign = utmCampaign === 'daily_signal' || utmCampaign === 'latest_command'
        ? utmCampaign
        : 'unknown';

      setReferral({
        isTelegramUser: true,
        campaign,
        leadId: leadId || undefined,
        hasShownWelcome,
      });

      // Track conversion event
      if (typeof window !== 'undefined' && !hasShownWelcome) {
        // Analytics tracking (Google Analytics, Mixpanel, etc.)
        if ((window as any).gtag) {
          (window as any).gtag('event', 'telegram_referral', {
            event_category: 'acquisition',
            event_label: campaign,
            lead_id: leadId,
          });
        }

        // Custom tracking
        console.log('[Telegram Referral]', {
          campaign,
          leadId,
          timestamp: new Date().toISOString(),
        });

        // Mark as shown
        sessionStorage.setItem('telegram_welcome_shown', 'true');
      }
    }
  }, [searchParams]);

  /**
   * Mark welcome message as shown
   */
  const markWelcomeShown = () => {
    sessionStorage.setItem('telegram_welcome_shown', 'true');
    setReferral((prev) => ({ ...prev, hasShownWelcome: true }));
  };

  /**
   * Track conversion action (signup, premium purchase)
   */
  const trackConversion = (action: 'signup' | 'premium' | 'view_details') => {
    if (!referral.isTelegramUser) return;

    if (typeof window !== 'undefined') {
      // Analytics tracking
      if ((window as any).gtag) {
        (window as any).gtag('event', 'telegram_conversion', {
          event_category: 'conversion',
          event_label: action,
          campaign: referral.campaign,
          lead_id: referral.leadId,
        });
      }

      console.log('[Telegram Conversion]', {
        action,
        campaign: referral.campaign,
        leadId: referral.leadId,
      });
    }
  };

  return {
    ...referral,
    markWelcomeShown,
    trackConversion,
  };
}

/**
 * Hook for mobile detection
 */
export function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    // Check if running in browser
    if (typeof window === 'undefined') return;

    // Initial check
    const checkMobile = () => {
      const userAgent = navigator.userAgent.toLowerCase();
      const isMobileDevice = /iphone|ipad|ipod|android|blackberry|windows phone/g.test(userAgent);
      const isSmallScreen = window.innerWidth <= 768;
      setIsMobile(isMobileDevice || isSmallScreen);
    };

    checkMobile();

    // Listen for resize
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return isMobile;
}
