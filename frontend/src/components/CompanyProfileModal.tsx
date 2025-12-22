"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  X,
  ExternalLink,
  TrendingUp,
  Zap,
  AlertTriangle,
  Calendar,
  DollarSign,
  Users,
  Briefcase,
  Lock,
  Sparkles,
} from "lucide-react"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import { cn } from "@/lib/cn"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import type { Company } from "./SignalTable"

interface CompanyProfileModalProps {
  company: Company
  isPremium: boolean
  open: boolean
  onClose: () => void
  onUpgrade: () => void
}

// Mock historical data for growth graph
const generateMockHistory = (currentScore: number) => {
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
  return months.map((month, i) => ({
    month,
    score: Math.max(0, currentScore - (6 - i) * 5 + Math.random() * 10),
  }))
}

const getTechCategory = (tech: string): string => {
  const categories: Record<string, string[]> = {
    backend: ["java", "spring", "node", "python", "django", "flask", "go", "rust"],
    frontend: ["react", "vue", "angular", "next", "svelte", "typescript"],
    database: ["postgres", "mysql", "mongodb", "redis", "elasticsearch"],
    cloud: ["aws", "azure", "gcp", "kubernetes", "docker"],
    ai: ["tensorflow", "pytorch", "openai", "machine learning", "ai"],
  }

  const techLower = tech.toLowerCase()
  for (const [category, keywords] of Object.entries(categories)) {
    if (keywords.some(keyword => techLower.includes(keyword))) {
      return category
    }
  }
  return "other"
}

const getCategoryColor = (category: string): string => {
  const colors: Record<string, string> = {
    backend: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    frontend: "bg-purple-500/10 text-purple-400 border-purple-500/20",
    database: "bg-green-500/10 text-green-400 border-green-500/20",
    cloud: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    ai: "bg-pink-500/10 text-pink-400 border-pink-500/20",
    other: "bg-gray-500/10 text-gray-400 border-gray-500/20",
  }
  return colors[category] || colors.other
}

export function CompanyProfileModal({
  company,
  isPremium,
  open,
  onClose,
  onUpgrade,
}: CompanyProfileModalProps) {
  const historyData = React.useMemo(
    () => generateMockHistory(company.pulse_score),
    [company.pulse_score]
  )

  const getDesperationColor = (level: string) => {
    switch (level) {
      case "CRITICAL": return "text-red-500"
      case "HIGH": return "text-amber-500"
      case "MODERATE": return "text-blue-500"
      default: return "text-gray-500"
    }
  }

  const groupedTechStack = React.useMemo(() => {
    const grouped: Record<string, string[]> = {}
    company.tech_stack?.forEach((tech) => {
      const category = getTechCategory(tech)
      if (!grouped[category]) grouped[category] = []
      grouped[category].push(tech)
    })
    return grouped
  }, [company.tech_stack])

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 z-50 backdrop-blur-sm"
          />

          {/* Slide-over Panel */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 h-full w-full max-w-2xl bg-gray-950 border-l border-gray-800 z-50 overflow-y-auto"
          >
            {/* Header */}
            <div className="sticky top-0 bg-gray-950/95 backdrop-blur-lg border-b border-gray-800 p-6 flex items-start justify-between z-10">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h2 className="text-2xl font-bold">{company.company_name}</h2>
                  {company.has_red_flags && (
                    <Badge variant="destructive" className="gap-1">
                      <AlertTriangle className="w-3 h-3" />
                      Red Flag
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  {company.website_url && (
                    <a
                      href={company.website_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 hover:text-primary transition-colors"
                    >
                      <ExternalLink className="w-3 h-3" />
                      Website
                    </a>
                  )}
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    Last seen: {new Date(company.last_seen).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="hover:bg-gray-900"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-8">
              {/* Signal Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-muted-foreground mb-2">
                    <Zap className="w-4 h-4" />
                    <span className="text-sm">Signal Strength</span>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold">{company.pulse_score.toFixed(0)}</span>
                    <span className="text-muted-foreground">/100</span>
                  </div>
                  <Badge className={cn("mt-2", getDesperationColor(company.desperation_level))}>
                    {company.desperation_level}
                  </Badge>
                </div>

                <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-muted-foreground mb-2">
                    <TrendingUp className="w-4 h-4" />
                    <span className="text-sm">Hiring Probability</span>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold text-green-500">
                      {company.hiring_probability.toFixed(0)}%
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    {company.urgency}
                  </p>
                </div>

                <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-muted-foreground mb-2">
                    <Briefcase className="w-4 h-4" />
                    <span className="text-sm">Expansion Density</span>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold">
                      {company.expansion_density.toFixed(0)}%
                    </span>
                  </div>
                  <div className="mt-2 bg-gray-800 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                      style={{ width: `${Math.min(company.expansion_density, 100)}%` }}
                    />
                  </div>
                </div>

                <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-muted-foreground mb-2">
                    <DollarSign className="w-4 h-4" />
                    <span className="text-sm">Funding</span>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold">
                      {company.funding_amount > 0
                        ? `$${(company.funding_amount / 1000000).toFixed(1)}M`
                        : "N/A"}
                    </span>
                  </div>
                  {company.funding_date && (
                    <p className="text-xs text-muted-foreground mt-2">
                      {new Date(company.funding_date).toLocaleDateString()}
                    </p>
                  )}
                </div>
              </div>

              {/* AI Recommendation */}
              <div className="bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-purple-500/20 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className="w-5 h-5 text-purple-400" />
                  <h3 className="font-semibold text-purple-400">AI Recommendation</h3>
                </div>
                <p className="text-sm leading-relaxed">{company.recommendation}</p>
              </div>

              {/* Growth Trend Chart */}
              <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-500" />
                  Signal Strength Trend
                </h3>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={historyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis
                      dataKey="month"
                      stroke="#9CA3AF"
                      style={{ fontSize: "12px" }}
                    />
                    <YAxis
                      stroke="#9CA3AF"
                      style={{ fontSize: "12px" }}
                      domain={[0, 100]}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#1F2937",
                        border: "1px solid #374151",
                        borderRadius: "8px",
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="score"
                      stroke="#8B5CF6"
                      strokeWidth={2}
                      dot={{ fill: "#8B5CF6", r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Tech Stack */}
              <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Technology Stack
                </h3>
                <div className="space-y-4">
                  {Object.entries(groupedTechStack).map(([category, technologies]) => (
                    <div key={category}>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide mb-2">
                        {category}
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {technologies.map((tech, i) => (
                          <Badge
                            key={i}
                            variant="outline"
                            className={cn("text-xs border", getCategoryColor(category))}
                          >
                            {tech}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Contact Information (Paywall) */}
              <div className="relative bg-gray-900/50 border border-gray-800 rounded-lg p-6">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Contact Information
                </h3>

                {!isPremium ? (
                  <>
                    {/* Blurred Content */}
                    <div className="relative">
                      <div className="blur-sm select-none pointer-events-none">
                        <div className="space-y-3">
                          <div className="flex items-center gap-3">
                            <span className="text-sm text-muted-foreground w-24">Email:</span>
                            <span className="text-sm">contact@company.com</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-sm text-muted-foreground w-24">Phone:</span>
                            <span className="text-sm">+1 (555) 123-4567</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-sm text-muted-foreground w-24">Decision Maker:</span>
                            <span className="text-sm">John Doe, CTO</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-sm text-muted-foreground w-24">LinkedIn:</span>
                            <span className="text-sm">linkedin.com/in/johndoe</span>
                          </div>
                        </div>
                      </div>

                      {/* Lock Overlay */}
                      <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <Lock className="w-12 h-12 text-muted-foreground mb-4" />
                        <p className="text-sm font-medium text-center mb-4">
                          Upgrade to Premium to unlock contact information
                        </p>
                        <Button onClick={onUpgrade} className="gap-2">
                          <Sparkles className="w-4 h-4" />
                          Upgrade to Premium
                        </Button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-muted-foreground w-24">Email:</span>
                      <span className="text-sm">contact@company.com</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-muted-foreground w-24">Phone:</span>
                      <span className="text-sm">+1 (555) 123-4567</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-muted-foreground w-24">Decision Maker:</span>
                      <span className="text-sm">John Doe, CTO</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-muted-foreground w-24">LinkedIn:</span>
                      <a
                        href="https://linkedin.com/in/johndoe"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-primary hover:underline flex items-center gap-1"
                      >
                        linkedin.com/in/johndoe
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
