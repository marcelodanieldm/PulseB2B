"use client"

import * as React from "react"
import { Check, Sparkles, Lock, Zap, TrendingUp, Download, Bell } from "lucide-react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/cn"

interface SubscriptionModalProps {
  open: boolean
  onClose: () => void
}

const features = [
  {
    icon: Lock,
    title: "Unlock All Contact Information",
    description: "Access emails, phone numbers, and decision maker details for high-scoring leads",
  },
  {
    icon: Bell,
    title: "Real-Time Alerts",
    description: "Get instant Telegram notifications when critical signals (90+) are detected",
  },
  {
    icon: TrendingUp,
    title: "Advanced Analytics",
    description: "Historical trend analysis, hiring probability forecasts, and expansion insights",
  },
  {
    icon: Download,
    title: "Export & API Access",
    description: "Download CSV reports and integrate with your CRM via REST API",
  },
  {
    icon: Zap,
    title: "Priority Processing",
    description: "Your target companies analyzed first with faster refresh rates",
  },
  {
    icon: Sparkles,
    title: "AI-Powered Recommendations",
    description: "Personalized outreach strategies and optimal timing suggestions",
  },
]

export function SubscriptionModal({ open, onClose }: SubscriptionModalProps) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 to-blue-500">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <div>
              <DialogTitle className="text-2xl">Upgrade to Premium</DialogTitle>
              <p className="text-sm text-muted-foreground mt-1">
                Unlock the full power of PulseB2B Intelligence
              </p>
            </div>
          </div>
        </DialogHeader>

        {/* Pricing */}
        <div className="mt-6 bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-purple-500/20 rounded-lg p-8 text-center">
          <Badge className="mb-4 bg-purple-500/20 text-purple-300 border-purple-500/30">
            Limited Time Offer
          </Badge>
          <div className="flex items-baseline justify-center gap-2 mb-2">
            <span className="text-5xl font-bold">$49</span>
            <span className="text-muted-foreground">/month</span>
          </div>
          <p className="text-sm text-muted-foreground mb-6">
            Billed monthly • Cancel anytime
          </p>
          
          <Button
            size="lg"
            className="w-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white font-semibold text-lg h-12"
          >
            <Sparkles className="w-5 h-5 mr-2" />
            Start Premium Trial
          </Button>
          
          <p className="text-xs text-muted-foreground mt-3">
            7-day free trial • No credit card required
          </p>
        </div>

        {/* Features Grid */}
        <div className="mt-8">
          <h3 className="font-semibold text-lg mb-4">Everything in Premium:</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {features.map((feature, index) => (
              <div
                key={index}
                className="flex gap-3 p-4 rounded-lg border border-gray-800 bg-gray-900/50 hover:bg-gray-900 transition-colors"
              >
                <div className={cn(
                  "flex h-10 w-10 shrink-0 items-center justify-center rounded-lg",
                  "bg-gradient-to-br from-purple-500/20 to-blue-500/20"
                )}>
                  <feature.icon className="h-5 w-5 text-purple-400" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-sm mb-1">{feature.title}</h4>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="mt-8 grid grid-cols-3 gap-4 p-4 bg-gray-900/50 rounded-lg border border-gray-800">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-400">10,000+</div>
            <div className="text-xs text-muted-foreground mt-1">Companies Tracked</div>
          </div>
          <div className="text-center border-l border-r border-gray-800">
            <div className="text-2xl font-bold text-blue-400">95%</div>
            <div className="text-xs text-muted-foreground mt-1">Accuracy Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">24/7</div>
            <div className="text-xs text-muted-foreground mt-1">Live Monitoring</div>
          </div>
        </div>

        {/* Comparison */}
        <div className="mt-8 border border-gray-800 rounded-lg overflow-hidden">
          <div className="grid grid-cols-2">
            <div className="p-4 bg-gray-900/50 border-r border-gray-800">
              <p className="font-semibold text-sm mb-3">Free Plan</p>
              <ul className="space-y-2 text-xs text-muted-foreground">
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 shrink-0 mt-0.5 text-gray-600" />
                  <span>View signal scores (blurred contacts)</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 shrink-0 mt-0.5 text-gray-600" />
                  <span>Basic company profiles</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 shrink-0 mt-0.5 text-gray-600" />
                  <span>Limited to 10 views/day</span>
                </li>
              </ul>
            </div>
            <div className="p-4 bg-gradient-to-br from-purple-900/10 to-blue-900/10">
              <p className="font-semibold text-sm mb-3 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-400" />
                Premium Plan
              </p>
              <ul className="space-y-2 text-xs">
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 shrink-0 mt-0.5 text-green-500" />
                  <span className="font-medium">Full contact information access</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 shrink-0 mt-0.5 text-green-500" />
                  <span className="font-medium">Unlimited views & exports</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 shrink-0 mt-0.5 text-green-500" />
                  <span className="font-medium">Real-time Telegram alerts</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="w-4 h-4 shrink-0 mt-0.5 text-green-500" />
                  <span className="font-medium">API access & integrations</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Trust Signals */}
        <div className="mt-6 flex items-center justify-center gap-8 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-green-500" />
            <span>Cancel anytime</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-green-500" />
            <span>Secure payments</span>
          </div>
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-green-500" />
            <span>Money-back guarantee</span>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
