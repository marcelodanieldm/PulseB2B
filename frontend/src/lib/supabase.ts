/**
 * Supabase client configuration
 */

import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Database types (generated from schema)
export interface Database {
  public: {
    Tables: {
      watchlist: {
        Row: {
          id: string;
          company_name: string;
          careers_url: string;
          region: string;
          priority: number;
          is_active: boolean;
          last_scraped_at: string | null;
          created_at: string;
          updated_at: string;
        };
      };
      jobs: {
        Row: {
          id: string;
          company_id: string;
          title: string;
          location: string;
          department: string;
          job_url: string;
          scraped_at: string;
          is_active: boolean;
        };
      };
      hiring_predictions: {
        Row: {
          id: string;
          company_id: string;
          probability: number;
          confidence: string;
          label: string;
          reasons: string[];
          features: Record<string, number>;
          status: string;
          predicted_at: string;
          created_at: string;
        };
      };
    };
  };
}
