'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';
import { useAuth } from './useAuth';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const DEV_MODE = process.env.NEXT_PUBLIC_DEV_MODE === 'true';

/**
 * usePremiumStatus Hook
 * 
 * Checks the is_premium boolean in the users table to determine if user has active subscription
 * 
 * Usage:
 *   const { isPremium, loading, checkPremiumStatus } = usePremiumStatus();
 *   
 *   if (!isPremium) {
 *     return <GatedContent />;
 *   }
 */

interface PremiumStatusState {
  isPremium: boolean;
  loading: boolean;
  error: string | null;
}

interface UsePremiumStatusReturn extends PremiumStatusState {
  checkPremiumStatus: () => Promise<void>;
  refreshStatus: () => Promise<void>;
}

export function usePremiumStatus(): UsePremiumStatusReturn {
  const { user, isAuthenticated } = useAuth();
  
  const [state, setState] = useState<PremiumStatusState>({
    isPremium: false,
    loading: true,
    error: null,
  });

  /**
   * Check premium status from users table
   */
  const checkPremiumStatus = async () => {
    // DEV MODE: Always premium
    if (DEV_MODE) {
      setState({
        isPremium: true,
        loading: false,
        error: null,
      });
      return;
    }
    
    // Not authenticated = not premium
    if (!isAuthenticated || !user) {
      setState({
        isPremium: false,
        loading: false,
        error: null,
      });
      return;
    }

    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      const supabase = createClient(supabaseUrl, supabaseAnonKey);
      const { data, error } = await supabase
        .from('users')
        .select('is_premium, premium_until')
        .eq('id', user.id)
        .single();

      if (error) throw error;

      // Check if premium and not expired
      const isPremiumActive = data?.is_premium === true;
      const premiumUntil = data?.premium_until ? new Date(data.premium_until) : null;
      const isExpired = premiumUntil ? premiumUntil < new Date() : false;

      setState({
        isPremium: isPremiumActive && !isExpired,
        loading: false,
        error: null,
      });
    } catch (error) {
      console.error('Error checking premium status:', error);
      setState({
        isPremium: false,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to check premium status',
      });
    }
  };

  /**
   * Refresh premium status (useful after payment completion)
   */
  const refreshStatus = async () => {
    await checkPremiumStatus();
  };

  // Check premium status on mount and when user changes
  useEffect(() => {
    checkPremiumStatus();
  }, [user?.id, isAuthenticated]);

  return {
    ...state,
    checkPremiumStatus,
    refreshStatus,
  };
}
