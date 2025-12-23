/**
 * Authentication and Premium Status Hook
 * Supports Google OAuth and Email/Password authentication
 * Checks Supabase auth and user's is_premium flag
 * 
 * DEV MODE: Set NEXT_PUBLIC_DEV_MODE=true to bypass authentication
 */

import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const DEV_MODE = process.env.NEXT_PUBLIC_DEV_MODE === 'true';

export interface AuthUser {
  id: string;
  email: string;
  isPremium: boolean;
  firstName?: string;
  lastName?: string;
}

export interface UseAuthReturn {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isPremium: boolean;
  isLoading: boolean;
  error: string | null;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
  refreshAuth: () => Promise<void>;
}

// Mock user for development mode
const DEV_USER: AuthUser = {
  id: 'dev-user-123',
  email: 'dev@pulseb2b.com',
  isPremium: true,
  firstName: 'Developer',
  lastName: 'Mode',
};

export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const checkAuth = async () => {
    try {
      setError(null);
      
      // DEV MODE: Bypass authentication
      if (DEV_MODE) {
        console.log('🔧 DEV MODE: Authentication bypassed');
        setUser(DEV_USER);
        setIsLoading(false);
        return;
      }
      
      const supabase = createClient(supabaseUrl, supabaseAnonKey);
      
      // Get current session
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session?.user) {
        setUser(null);
        setIsLoading(false);
        return;
      }

      // Get user profile with premium status
      const { data: profile, error: profileError } = await supabase
        .from('users')
        .select('id, email, is_premium, first_name, last_name')
        .eq('id', session.user.id)
        .single();

      if (profileError) {
        console.error('Error fetching user profile:', profileError);
        // Fallback: user is authenticated but premium status unknown
        setUser({
          id: session.user.id,
          email: session.user.email || '',
          isPremium: false,
          firstName: session.user.user_metadata?.first_name,
          lastName: session.user.user_metadata?.last_name,
        });
      } else {
        setUser({
          id: profile.id,
          email: profile.email,
          isPremium: profile.is_premium || false,
          firstName: profile.first_name,
          lastName: profile.last_name,
        });
      }
    } catch (error) {
      console.error('Auth check error:', error);
      setUser(null);
      setError(error instanceof Error ? error.message : 'Auth check failed');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Sign in with email and password
   */
  const signIn = async (email: string, password: string) => {
    try {
      setError(null);
      setIsLoading(true);
      
      // DEV MODE: Auto sign in
      if (DEV_MODE) {
        console.log('🔧 DEV MODE: Auto sign in');
        setUser(DEV_USER);
        setIsLoading(false);
        return;
      }
      
      const supabase = createClient(supabaseUrl, supabaseAnonKey);
      
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;
      await checkAuth();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Sign in failed';
      setError(message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Sign up with email and password
   */
  const signUp = async (email: string, password: string) => {
    try {
      setError(null);
      setIsLoading(true);
      
      // DEV MODE: Auto sign up
      if (DEV_MODE) {
        console.log('🔧 DEV MODE: Auto sign up');
        setUser(DEV_USER);
        setIsLoading(false);
        return;
      }
      
      const supabase = createClient(supabaseUrl, supabaseAnonKey);
      
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: typeof window !== 'undefined' 
            ? `${window.location.origin}/auth/callback` 
            : undefined,
        },
      });

      if (error) throw error;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Sign up failed';
      setError(message);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Sign in with Google OAuth
   */
  const signInWithGoogle = async () => {
    try {
      setError(null);
      
      // DEV MODE: Auto sign in
      if (DEV_MODE) {
        console.log('🔧 DEV MODE: Google sign in bypassed');
        setUser(DEV_USER);
        return;
      }
      
      const supabase = createClient(supabaseUrl, supabaseAnonKey);
      
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: typeof window !== 'undefined'
            ? `${window.location.origin}/auth/callback`
            : undefined,
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          },
        },
      });

      if (error) throw error;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Google sign in failed';
      setError(message);
      throw error;
    }
  };

  const signOut = async () => {
    try {
      setError(null);
      
      // DEV MODE: Just clear user
      if (DEV_MODE) {
        console.log('🔧 DEV MODE: Sign out');
        setUser(null);
        return;
      }
      
      const supabase = createClient(supabaseUrl, supabaseAnonKey);
      await supabase.auth.signOut();
      setUser(null);
    } catch (error) {
      console.error('Sign out error:', error);
      setError(error instanceof Error ? error.message : 'Sign out failed');
    }
  };

  const refreshAuth = async () => {
    setIsLoading(true);
    await checkAuth();
  };

  useEffect(() => {
    checkAuth();

    // Subscribe to auth state changes
    const supabase = createClient(supabaseUrl, supabaseAnonKey);
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED') {
        checkAuth();
      } else if (event === 'SIGNED_OUT') {
        setUser(null);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  return {
    user,
    isAuthenticated: !!user,
    isPremium: user?.isPremium || false,
    isLoading,
    error,
    signIn,
    signUp,
    signInWithGoogle,
    signOut,
    refreshAuth,
  };
}
