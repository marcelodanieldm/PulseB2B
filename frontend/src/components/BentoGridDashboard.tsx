"use client";

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BlurredText, BlurredAccess } from "@/components/ui/blurred-text";
import {
  TrendingUp,
  DollarSign,
  Users,
  Globe,
  Zap,
  Rocket,
  Target,
  ChevronRight,
  Lock,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Opportunity {
  id: string;
  company_name: string;
  score: number;
  priority: "critical" | "high" | "medium" | "low";
  country: string;
  funding_stage?: string;
  funding_amount?: number;
  active_jobs: number;
  latest_funding_date?: string;
  industry?: string;
  factors: string[];
  contact_email?: string;
  contact_phone?: string;
  linkedin_url?: string;
}

interface OpportunityCardProps {
  opportunity: Opportunity;
  isAuthenticated: boolean;
  onSignUp: () => void;
  size?: "small" | "medium" | "large";
}

function OpportunityCard({
  opportunity,
  isAuthenticated,
  onSignUp,
  size = "medium",
}: OpportunityCardProps) {
  const getScoreGradient = (score: number) => {
    if (score >= 80) return "from-green-500 to-emerald-600";
    if (score >= 60) return "from-blue-500 to-cyan-600";
    if (score >= 40) return "from-yellow-500 to-orange-600";
    return "from-gray-500 to-slate-600";
  };

  const getPriorityBadge = (priority: string) => {
    const variants: Record<string, "critical" | "high" | "medium" | "low"> = {
      critical: "critical",
      high: "high",
      medium: "medium",
      low: "low",
    };
    return variants[priority] || "low";
  };

  const formatCurrency = (amount?: number) => {
    if (!amount) return "N/A";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      notation: "compact",
      maximumFractionDigits: 1,
    }).format(amount);
  };

  const getFlagEmoji = (country: string) => {
    const flags: Record<string, string> = {
      "United States": "🇺🇸",
      US: "🇺🇸",
      Brazil: "🇧🇷",
      Mexico: "🇲🇽",
      "United Kingdom": "🇬🇧",
      UK: "🇬🇧",
      Germany: "🇩🇪",
      France: "🇫🇷",
      Spain: "🇪🇸",
    };
    return flags[country] || "🌍";
  };

  return (
    <Card
      className={cn(
        "group relative overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 border-2",
        opportunity.priority === "critical" && "border-red-200",
        opportunity.priority === "high" && "border-orange-200",
        size === "large" && "md:col-span-2 md:row-span-2",
        size === "medium" && "md:col-span-1 md:row-span-1"
      )}
    >
      {/* Score Badge - Top Right */}
      <div className="absolute top-4 right-4 z-20">
        <div
          className={cn(
            "flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br shadow-lg text-white font-bold text-xl",
            getScoreGradient(opportunity.score)
          )}
        >
          {opportunity.score}
        </div>
      </div>

      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4 pr-20">
          <div className="space-y-2 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-2xl">{getFlagEmoji(opportunity.country)}</span>
              <Badge variant={getPriorityBadge(opportunity.priority)}>
                {opportunity.priority.toUpperCase()}
              </Badge>
            </div>
            <CardTitle className="text-2xl font-bold group-hover:text-blue-600 transition-colors">
              {opportunity.company_name}
            </CardTitle>
            {opportunity.industry && (
              <p className="text-sm text-muted-foreground">{opportunity.industry}</p>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Funding Info */}
        {opportunity.funding_stage && (
          <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg">
            <Rocket className="w-5 h-5 text-blue-600" />
            <div>
              <p className="text-xs text-muted-foreground">Funding Stage</p>
              <p className="font-semibold text-blue-900">{opportunity.funding_stage}</p>
            </div>
            {opportunity.funding_amount && (
              <div className="ml-auto text-right">
                <p className="text-xs text-muted-foreground">Amount</p>
                <p className="font-semibold text-blue-900">
                  {formatCurrency(opportunity.funding_amount)}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Active Jobs */}
        <div className="flex items-center gap-2 p-3 bg-purple-50 rounded-lg">
          <Users className="w-5 h-5 text-purple-600" />
          <div>
            <p className="text-xs text-muted-foreground">Active Jobs</p>
            <p className="font-semibold text-purple-900">
              {opportunity.active_jobs} open positions
            </p>
          </div>
        </div>

        {/* Offshore Potential */}
        <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg">
          <Globe className="w-5 h-5 text-green-600" />
          <div className="flex-1">
            <p className="text-xs text-muted-foreground">Offshore Potential</p>
            <p className="font-semibold text-green-900">High Growth Opportunity</p>
          </div>
          <Zap className="w-5 h-5 text-yellow-500" />
        </div>

        {/* Key Factors */}
        {size === "large" && opportunity.factors.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-semibold flex items-center gap-2">
              <Target className="w-4 h-4" />
              Key Signals
            </p>
            <ul className="space-y-1">
              {opportunity.factors.slice(0, 3).map((factor, idx) => (
                <li key={idx} className="text-sm text-muted-foreground flex items-center gap-2">
                  <ChevronRight className="w-3 h-3 text-blue-600" />
                  {factor}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Contact Info - Blurred */}
        <BlurredAccess isBlurred={!isAuthenticated} onSignUp={onSignUp}>
          <div className="space-y-2 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center gap-2 text-sm">
              <Lock className="w-4 h-4 text-gray-400" />
              <span className="font-semibold text-gray-700">Contact Information</span>
            </div>
            <div className="space-y-1 text-sm">
              <p className="text-muted-foreground">
                Email:{" "}
                <BlurredText
                  isBlurred={!isAuthenticated}
                  className="text-blue-600 font-mono"
                >
                  {opportunity.contact_email || "contact@company.com"}
                </BlurredText>
              </p>
              <p className="text-muted-foreground">
                Phone:{" "}
                <BlurredText
                  isBlurred={!isAuthenticated}
                  className="text-blue-600 font-mono"
                >
                  {opportunity.contact_phone || "+1 (555) 123-4567"}
                </BlurredText>
              </p>
            </div>
          </div>
        </BlurredAccess>

        {/* Action Button */}
        <button
          onClick={onSignUp}
          className="w-full mt-4 py-2 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all duration-300 hover:scale-105 flex items-center justify-center gap-2"
        >
          View Full Profile
          <ChevronRight className="w-4 h-4" />
        </button>
      </CardContent>
    </Card>
  );
}

interface BentoGridDashboardProps {
  opportunities: Opportunity[];
  isAuthenticated?: boolean;
  onSignUp?: () => void;
}

export function BentoGridDashboard({
  opportunities,
  isAuthenticated = false,
  onSignUp = () => console.log("Sign up clicked"),
}: BentoGridDashboardProps) {
  // Separate opportunities by region
  const usOpportunities = opportunities.filter(
    (o) => o.country === "United States" || o.country === "US"
  );
  const brazilOpportunities = opportunities.filter((o) => o.country === "Brazil");
  const europeOpportunities = opportunities.filter(
    (o) => ["United Kingdom", "UK", "Germany", "France", "Spain"].includes(o.country)
  );

  return (
    <div className="space-y-8">
      {/* US Market */}
      {usOpportunities.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
              <span className="text-2xl">🇺🇸</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold">US Tech Market</h2>
              <p className="text-sm text-muted-foreground">
                {usOpportunities.length} hot opportunities
              </p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {usOpportunities.slice(0, 3).map((opp, idx) => (
              <OpportunityCard
                key={opp.id}
                opportunity={opp}
                isAuthenticated={isAuthenticated}
                onSignUp={onSignUp}
                size={idx === 0 ? "large" : "medium"}
              />
            ))}
          </div>
        </section>
      )}

      {/* Brazil Market */}
      {brazilOpportunities.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
              <span className="text-2xl">🇧🇷</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold">Brazil Expansion</h2>
              <p className="text-sm text-muted-foreground">
                {brazilOpportunities.length} offshore opportunities
              </p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {brazilOpportunities.slice(0, 3).map((opp) => (
              <OpportunityCard
                key={opp.id}
                opportunity={opp}
                isAuthenticated={isAuthenticated}
                onSignUp={onSignUp}
              />
            ))}
          </div>
        </section>
      )}

      {/* Europe Market */}
      {europeOpportunities.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
              <span className="text-2xl">🇪🇺</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold">European Market</h2>
              <p className="text-sm text-muted-foreground">
                {europeOpportunities.length} venture-backed startups
              </p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {europeOpportunities.slice(0, 3).map((opp) => (
              <OpportunityCard
                key={opp.id}
                opportunity={opp}
                isAuthenticated={isAuthenticated}
                onSignUp={onSignUp}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
