/**
 * Unlock Premium Modal
 * Shows Stripe payment link and premium benefits
 */

'use client';

import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Lock,
  Check,
  Zap,
  Mail,
  Phone,
  DollarSign,
  Users,
  TrendingUp,
  ExternalLink,
  Crown,
  Shield,
  BarChart3,
} from 'lucide-react';
import { cn } from '@/lib/cn';

interface UnlockPremiumModalProps {
  isOpen: boolean;
  onClose: () => void;
  stripePaymentLink?: string;
}

const premiumFeatures = [
  {
    icon: Mail,
    title: 'Decision Maker Emails',
    description: 'Direct contact emails for CEOs, CTOs, and Hiring Managers',
    badge: 'Most Popular',
  },
  {
    icon: Phone,
    title: 'Direct Phone Numbers',
    description: 'Verified phone numbers for immediate outreach',
    badge: null,
  },
  {
    icon: DollarSign,
    title: 'Detailed Funding Data',
    description: 'Complete funding rounds, investors, and valuation history',
    badge: null,
  },
  {
    icon: Users,
    title: 'Team Insights',
    description: 'Leadership changes, departures, and hiring velocity',
    badge: null,
  },
  {
    icon: TrendingUp,
    title: 'Advanced Analytics',
    description: 'Tech stack changes, expansion signals, and growth metrics',
    badge: null,
  },
  {
    icon: BarChart3,
    title: 'Real-Time Alerts',
    description: 'Get notified when high-probability opportunities emerge',
    badge: 'New',
  },
];

const pricingTier = {
  name: 'Premium',
  price: '$99',
  period: 'month',
  description: 'Unlock all premium intelligence data',
  features: [
    'Unlimited contact emails',
    'Verified phone numbers',
    'Complete funding history',
    'Team movement tracking',
    'Priority support',
    'Export to CSV',
    'API access',
  ],
};

export function UnlockPremiumModal({
  isOpen,
  onClose,
  stripePaymentLink = 'https://buy.stripe.com/test_demo_link',
}: UnlockPremiumModalProps) {
  const handleUpgrade = () => {
    // Open Stripe payment link in new tab
    window.open(stripePaymentLink, '_blank', 'noopener,noreferrer');
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-to-br from-amber-500 to-orange-500 rounded-lg">
              <Crown className="w-6 h-6 text-white" />
            </div>
            <div>
              <DialogTitle className="text-2xl">Unlock Premium Intelligence</DialogTitle>
              <DialogDescription className="text-base mt-1">
                Access decision maker contacts, funding details, and advanced analytics
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        {/* Premium Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          {premiumFeatures.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <div
                key={idx}
                className="flex gap-4 p-4 rounded-lg border border-border hover:border-amber-500/50 transition-colors group"
              >
                <div className="p-2 bg-amber-500/10 rounded-lg h-fit group-hover:bg-amber-500/20 transition-colors">
                  <Icon className="w-5 h-5 text-amber-500" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-semibold text-sm">{feature.title}</h4>
                    {feature.badge && (
                      <Badge variant="secondary" className="text-xs px-2 py-0">
                        {feature.badge}
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {feature.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Pricing Card */}
        <div className="mt-8 p-6 rounded-xl border-2 border-amber-500/30 bg-gradient-to-br from-amber-500/5 to-orange-500/5">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h3 className="text-2xl font-bold flex items-center gap-2">
                {pricingTier.name}
                <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white">
                  Limited Offer
                </Badge>
              </h3>
              <p className="text-muted-foreground mt-1">
                {pricingTier.description}
              </p>
            </div>
            <div className="text-right">
              <div className="flex items-baseline gap-1">
                <span className="text-4xl font-bold">{pricingTier.price}</span>
                <span className="text-muted-foreground">/{pricingTier.period}</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Cancel anytime
              </p>
            </div>
          </div>

          {/* Features List */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
            {pricingTier.features.map((feature, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <div className="p-0.5 bg-green-500 rounded-full">
                  <Check className="w-3 h-3 text-white" />
                </div>
                <span className="text-sm">{feature}</span>
              </div>
            ))}
          </div>

          {/* CTA Button */}
          <Button
            onClick={handleUpgrade}
            size="lg"
            className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white shadow-lg hover:shadow-xl transition-all duration-200 gap-2"
          >
            <Zap className="w-5 h-5" />
            Upgrade to Premium Now
            <ExternalLink className="w-4 h-4" />
          </Button>

          {/* Trust Badges */}
          <div className="flex items-center justify-center gap-6 mt-6 pt-6 border-t border-border/50">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Shield className="w-4 h-4 text-green-500" />
              Secure Payment
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Lock className="w-4 h-4 text-blue-500" />
              30-Day Guarantee
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Zap className="w-4 h-4 text-amber-500" />
              Instant Access
            </div>
          </div>
        </div>

        {/* Fine Print */}
        <p className="text-xs text-center text-muted-foreground mt-4">
          By upgrading, you agree to our Terms of Service and Privacy Policy.
          <br />
          Subscription renews automatically. Cancel anytime from your account settings.
        </p>
      </DialogContent>
    </Dialog>
  );
}
