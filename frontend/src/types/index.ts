/**
 * Types for PulseB2B Dashboard
 */

// Traffic Light Status
export type TrafficLightStatus = 'red' | 'green' | 'golden' | 'blue';

export interface Company {
  id: string;
  name: string;
  region: string;
  country: string;
  city?: string;
  latitude: number;
  longitude: number;
  
  // Core metrics
  team_size: number;
  total_funding: number;
  last_funding_amount: number;
  last_funding_date: string;
  funding_stage: string;
  
  // ML Prediction
  hiring_probability: number;
  confidence: string;
  prediction_label: string;
  
  // Traffic Light
  status: TrafficLightStatus;
  status_reason: string;
  
  // Features
  funding_recency: number;
  tech_churn: number;
  job_post_velocity: number;
  region_factor: number;
  senior_departures: number;
  current_month_posts: number;
  
  // Metadata
  industry?: string;
  website?: string;
  logo_url?: string;
  description?: string;
  founded_date?: string;
  
  // Timestamps
  predicted_at: string;
  updated_at: string;
}

export interface PredictionReason {
  icon: string;
  text: string;
  impact: 'high' | 'medium' | 'low';
}

export interface CompanyPrediction {
  company_id: string;
  company_name: string;
  
  prediction: {
    probability: number;
    class: number;
    label: string;
    confidence: string;
  };
  
  reasons: string[];
  
  features: {
    funding_recency: number;
    tech_churn: number;
    job_post_velocity: number;
    region_factor: number;
    senior_departures: number;
    current_month_posts: number;
    tech_roles_ratio: number;
  };
  
  shap_explanation?: Array<{
    feature: string;
    value: number;
    impact: number;
  }>;
  
  metadata: {
    model_type: string;
    predicted_at: string;
    prediction_horizon: string;
  };
}

export interface GrowthMetrics {
  date: string;
  team_size: number;
  funding: number;
  job_posts: number;
  probability: number;
}

export interface CompanyWithGrowth extends Company {
  growth_history: GrowthMetrics[];
}

// Map filters
export interface MapFilters {
  status: TrafficLightStatus[];
  minProbability: number;
  maxProbability: number;
  regions: string[];
  fundingStages: string[];
  minFunding: number;
  maxFunding: number;
}

// Dashboard stats
export interface DashboardStats {
  total_companies: number;
  high_probability: number;
  medium_probability: number;
  low_probability: number;
  average_probability: number;
  
  by_status: {
    red: number;
    green: number;
    golden: number;
    blue: number;
  };
  
  by_region: Record<string, number>;
  
  top_opportunities: Company[];
  recent_funding: Company[];
  high_risk: Company[];
}

// Chart data
export interface ChartDataPoint {
  name: string;
  value: number;
  fill?: string;
}

export interface TimeSeriesPoint {
  date: string;
  [key: string]: string | number;
}

// API responses
export interface ApiResponse<T> {
  data: T;
  error?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
}
