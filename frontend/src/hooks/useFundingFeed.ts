import useSWR from "swr"
import { createClient } from "@/lib/supabase"

export interface FundingSignal {
  id: string
  company_name: string
  pulse_score: number
  desperation_level: "CRITICAL" | "HIGH" | "MODERATE" | "LOW"
  urgency: string
  hiring_probability: number
  expansion_density: number
  tech_stack: string[]
  funding_amount: number
  funding_date: string
  last_seen: string
  has_red_flags: boolean
  website_url?: string
  recommendation: string
  created_at: string
}

interface UseFundingFeedOptions {
  minScore?: number
  refreshInterval?: number
  limit?: number
}

const fetcher = async (url: string) => {
  const supabase = createClient()
  const minScore = parseInt(url.split("minScore=")[1]?.split("&")[0] || "40")
  const limit = parseInt(url.split("limit=")[1] || "100")

  const { data, error } = await supabase
    .from("oracle_predictions")
    .select("*")
    .gte("pulse_score", minScore)
    .order("pulse_score", { ascending: false })
    .order("last_seen", { ascending: false })
    .limit(limit)

  if (error) throw error
  return data as FundingSignal[]
}

export function useFundingFeed(options: UseFundingFeedOptions = {}) {
  const {
    minScore = 40,
    refreshInterval = 30000, // 30 seconds
    limit = 100,
  } = options

  const { data, error, isLoading, mutate } = useSWR<FundingSignal[]>(
    `/api/funding-feed?minScore=${minScore}&limit=${limit}`,
    fetcher,
    {
      refreshInterval,
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
      dedupingInterval: 5000,
    }
  )

  return {
    signals: data || [],
    isLoading,
    isError: error,
    refresh: mutate,
  }
}

// Hook for critical signals (90+)
export function useCriticalSignals() {
  return useFundingFeed({
    minScore: 90,
    refreshInterval: 15000, // 15 seconds for critical
    limit: 50,
  })
}

// Hook for high-priority signals (60-89)
export function useHighPrioritySignals() {
  return useFundingFeed({
    minScore: 60,
    refreshInterval: 30000,
    limit: 100,
  })
}

// Hook for single company updates
export function useCompanySignal(companyId: string) {
  const supabase = createClient()

  const fetcher = async () => {
    const { data, error } = await supabase
      .from("oracle_predictions")
      .select("*")
      .eq("id", companyId)
      .single()

    if (error) throw error
    return data as FundingSignal
  }

  const { data, error, isLoading, mutate } = useSWR<FundingSignal>(
    companyId ? `/api/company/${companyId}` : null,
    fetcher,
    {
      refreshInterval: 60000, // 1 minute
      revalidateOnFocus: true,
    }
  )

  return {
    company: data,
    isLoading,
    isError: error,
    refresh: mutate,
  }
}
