"use client";

import { Suspense } from "react";
import { BentoGridDashboard } from "@/components/BentoGridDashboard";
import { TrendingUp, Zap, Globe, ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

// Mock data - replace with real Supabase data in production
const mockOpportunities = [
  {
    id: "1",
    company_name: "OpenAI",
    score: 95,
    priority: "critical" as const,
    country: "United States",
    funding_stage: "Series C",
    funding_amount: 10000000000,
    active_jobs: 24,
    latest_funding_date: "2024-01-15",
    industry: "Artificial Intelligence",
    factors: [
      "Recent funding (< 90 days): +50",
      "Large funding round (> $50M): +30",
      "Active job postings (24): +15",
    ],
    contact_email: "talent@openai.com",
    contact_phone: "+1 (415) 555-0100",
    linkedin_url: "https://linkedin.com/company/openai",
  },
  {
    id: "2",
    company_name: "Stripe",
    score: 88,
    priority: "critical" as const,
    country: "United States",
    funding_stage: "Series H",
    funding_amount: 6500000000,
    active_jobs: 18,
    latest_funding_date: "2023-03-14",
    industry: "Fintech",
    factors: [
      "Large company expansion: +40",
      "Active LATAM hiring: +28",
      "Positive news sentiment: +20",
    ],
    contact_email: "hiring@stripe.com",
    contact_phone: "+1 (650) 555-0200",
  },
  {
    id: "3",
    company_name: "Databricks",
    score: 82,
    priority: "high" as const,
    country: "United States",
    funding_stage: "Series H",
    funding_amount: 3800000000,
    active_jobs: 15,
    industry: "Data & Analytics",
    factors: [
      "Recent funding: +50",
      "Job postings velocity: +20",
      "Offshore expansion mentioned: +12",
    ],
    contact_email: "careers@databricks.com",
    contact_phone: "+1 (415) 555-0300",
  },
  {
    id: "4",
    company_name: "Nubank",
    score: 78,
    priority: "high" as const,
    country: "Brazil",
    funding_stage: "Public (IPO)",
    funding_amount: 2600000000,
    active_jobs: 32,
    industry: "Fintech",
    factors: [
      "LATAM leader: +30",
      "High hiring velocity: +25",
      "Regional expansion: +23",
    ],
    contact_email: "trabalhe@nubank.com.br",
    contact_phone: "+55 11 4000-0400",
  },
  {
    id: "5",
    company_name: "Wildlife Studios",
    score: 72,
    priority: "high" as const,
    country: "Brazil",
    funding_stage: "Series B",
    funding_amount: 1200000000,
    active_jobs: 28,
    industry: "Gaming",
    factors: [
      "Fast-growing games company: +35",
      "LATAM tech hub: +22",
      "Active hiring: +15",
    ],
    contact_email: "jobs@wildlifestudios.com",
    contact_phone: "+55 11 3000-0500",
  },
  {
    id: "6",
    company_name: "Revolut",
    score: 85,
    priority: "critical" as const,
    country: "United Kingdom",
    funding_stage: "Series E",
    funding_amount: 5500000000,
    active_jobs: 21,
    industry: "Fintech",
    factors: [
      "European unicorn: +40",
      "Global expansion: +30",
      "High job velocity: +15",
    ],
    contact_email: "careers@revolut.com",
    contact_phone: "+44 20 7000 0600",
  },
];

function DashboardHeader() {
  return (
    <header className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                PulseB2B
              </h1>
              <p className="text-xs text-muted-foreground">Global Market Intelligence</p>
            </div>
          </div>
          <Button
            size="lg"
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
          >
            Get Started
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </div>
    </header>
  );
}

function StatsBar() {
  const stats = [
    {
      icon: TrendingUp,
      label: "Active Opportunities",
      value: "347",
      trend: "+12% this week",
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
    {
      icon: Zap,
      label: "Series A-C Funding",
      value: "$2.4B",
      trend: "Last 90 days",
      color: "text-purple-600",
      bg: "bg-purple-50",
    },
    {
      icon: Globe,
      label: "Markets Tracked",
      value: "12",
      trend: "US, LATAM, Europe",
      color: "text-green-600",
      bg: "bg-green-50",
    },
  ];

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stats.map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <Card key={idx} className="border-2">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="space-y-2 flex-1">
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <p className="text-3xl font-bold">{stat.value}</p>
                    <p className="text-xs text-muted-foreground">{stat.trend}</p>
                  </div>
                  <div className={`w-12 h-12 rounded-full ${stat.bg} flex items-center justify-center`}>
                    <Icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

function HeroSection() {
  return (
    <div className="bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 py-12">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            Discover Venture-Backed Companies
          </h2>
          <p className="text-xl text-muted-foreground">
            Real-time intelligence on US tech companies expanding globally. Track Series A-C funding,
            active hiring, and offshore potential.
          </p>
        </div>
      </div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {[1, 2, 3].map((section) => (
        <div key={section} className="space-y-4">
          <div className="h-8 w-48 bg-gray-200 rounded animate-pulse" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((card) => (
              <div key={card} className="h-96 bg-gray-200 rounded-xl animate-pulse" />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function DashboardPage() {
  const handleSignUp = () => {
    console.log("Sign up modal would open here");
    // TODO: Implement sign-up modal or redirect to /auth/signup
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <DashboardHeader />
      <HeroSection />
      <StatsBar />
      
      <main className="container mx-auto px-4 py-8">
        <Suspense fallback={<LoadingSkeleton />}>
          <BentoGridDashboard
            opportunities={mockOpportunities}
            isAuthenticated={false}
            onSignUp={handleSignUp}
          />
        </Suspense>
      </main>

      <footer className="border-t bg-white mt-16 py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>© 2024 PulseB2B. Powered by Ghost Infrastructure.</p>
          <p className="mt-2">Real-time data from SEC.gov, LinkedIn, and Google News</p>
        </div>
      </footer>
    </div>
  );
}
