/**
 * Premium Paywall Component
 * Stripe integration for "Unlock Full Data" painted door test
 */

'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Lock, 
  Unlock, 
  TrendingUp, 
  Database, 
  Zap, 
  Globe, 
  X,
  Check,
  CreditCard,
  Shield
} from 'lucide-react';

interface PremiumPaywallProps {
  isOpen: boolean;
  onClose: () => void;
}

// Stripe Test Mode Payment Link (Replace with your actual link)
const STRIPE_PAYMENT_LINK = 'https://buy.stripe.com/test_xxxxxxxxxxxxxx';

export default function PremiumPaywall({ isOpen, onClose }: PremiumPaywallProps) {
  const [selectedPlan, setSelectedPlan] = useState<'monthly' | 'annual'>('monthly');

  const handleUnlock = () => {
    // Track conversion intent (analytics)
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'begin_checkout', {
        currency: 'USD',
        value: selectedPlan === 'monthly' ? 299 : 2990,
        items: [{
          item_id: `premium-${selectedPlan}`,
          item_name: `PulseB2B Premium ${selectedPlan === 'monthly' ? 'Monthly' : 'Annual'}`,
          price: selectedPlan === 'monthly' ? 299 : 2990,
        }]
      });
    }

    // Redirect to Stripe (Painted Door Test)
    window.open(STRIPE_PAYMENT_LINK, '_blank');
  };

  const features = [
    {
      icon: <Database className="w-5 h-5" />,
      title: 'Full Venture Database',
      description: 'Access to 10,000+ US, Brazil, and Mexico ventures',
    },
    {
      icon: <TrendingUp className="w-5 h-5" />,
      title: 'Real-Time Signals',
      description: 'Live hiring signals updated every 12 hours via GitHub Actions',
    },
    {
      icon: <Zap className="w-5 h-5" />,
      title: 'Critical Alerts',
      description: 'Telegram notifications for 85%+ hiring probability ventures',
    },
    {
      icon: <Globe className="w-5 h-5" />,
      title: 'Offshore Scoring',
      description: 'ML-powered offshore potential analysis with tech stack detection',
    },
    {
      icon: <Shield className="w-5 h-5" />,
      title: 'API Access',
      description: 'REST API for CRM integration and automated workflows',
    },
    {
      icon: <CreditCard className="w-5 h-5" />,
      title: 'Export & Reports',
      description: 'CSV/JSON exports and custom market intelligence reports',
    },
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              {/* Header */}
              <div className="relative bg-gradient-to-r from-blue-600 to-purple-600 text-white p-8 rounded-t-2xl">
                <button
                  onClick={onClose}
                  className="absolute top-6 right-6 text-white/80 hover:text-white transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>

                <div className="flex items-start gap-4">
                  <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                    <Lock className="w-8 h-8" />
                  </div>
                  <div>
                    <h2 className="text-3xl font-bold mb-2">Unlock Full Intelligence</h2>
                    <p className="text-blue-100 text-lg">
                      Get unlimited access to premium venture data and real-time hiring signals
                    </p>
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="p-8">
                {/* Pricing Toggle */}
                <div className="flex justify-center mb-8">
                  <div className="inline-flex bg-gray-100 rounded-xl p-1">
                    <button
                      onClick={() => setSelectedPlan('monthly')}
                      className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                        selectedPlan === 'monthly'
                          ? 'bg-white text-gray-900 shadow-md'
                          : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      Monthly
                    </button>
                    <button
                      onClick={() => setSelectedPlan('annual')}
                      className={`px-6 py-3 rounded-lg font-semibold transition-all relative ${
                        selectedPlan === 'annual'
                          ? 'bg-white text-gray-900 shadow-md'
                          : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      Annual
                      <span className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-0.5 rounded-full">
                        Save 20%
                      </span>
                    </button>
                  </div>
                </div>

                {/* Pricing Cards */}
                <div className="grid md:grid-cols-2 gap-6 mb-8">
                  {/* Free Plan */}
                  <div className="border-2 border-gray-200 rounded-xl p-6">
                    <div className="mb-4">
                      <h3 className="text-xl font-bold text-gray-900 mb-2">Free Tier</h3>
                      <div className="flex items-baseline gap-2">
                        <span className="text-4xl font-bold text-gray-900">$0</span>
                        <span className="text-gray-600">/month</span>
                      </div>
                    </div>
                    <ul className="space-y-3">
                      <li className="flex items-start gap-2 text-sm text-gray-600">
                        <Check className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                        <span>View all venture locations</span>
                      </li>
                      <li className="flex items-start gap-2 text-sm text-gray-600">
                        <Check className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                        <span>See signal strength (up to 70%)</span>
                      </li>
                      <li className="flex items-start gap-2 text-sm text-gray-600">
                        <Check className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                        <span>Limited company details</span>
                      </li>
                      <li className="flex items-start gap-2 text-sm text-gray-400 line-through">
                        <X className="w-5 h-5 flex-shrink-0 mt-0.5" />
                        <span>High-priority signals (70%+)</span>
                      </li>
                      <li className="flex items-start gap-2 text-sm text-gray-400 line-through">
                        <X className="w-5 h-5 flex-shrink-0 mt-0.5" />
                        <span>Real-time Telegram alerts</span>
                      </li>
                      <li className="flex items-start gap-2 text-sm text-gray-400 line-through">
                        <X className="w-5 h-5 flex-shrink-0 mt-0.5" />
                        <span>Export & API access</span>
                      </li>
                    </ul>
                  </div>

                  {/* Premium Plan */}
                  <div className="border-2 border-blue-500 rounded-xl p-6 bg-gradient-to-br from-blue-50 to-purple-50 relative overflow-hidden">
                    <div className="absolute top-0 right-0 bg-blue-500 text-white text-xs font-bold px-3 py-1 rounded-bl-lg">
                      RECOMMENDED
                    </div>
                    <div className="mb-4">
                      <h3 className="text-xl font-bold text-gray-900 mb-2">Premium</h3>
                      <div className="flex items-baseline gap-2">
                        <span className="text-4xl font-bold text-gray-900">
                          ${selectedPlan === 'monthly' ? '299' : '239'}
                        </span>
                        <span className="text-gray-600">/month</span>
                      </div>
                      {selectedPlan === 'annual' && (
                        <p className="text-sm text-green-600 font-semibold mt-1">
                          Billed annually at $2,868 (save $720/year)
                        </p>
                      )}
                    </div>
                    <ul className="space-y-3">
                      <li className="flex items-start gap-2 text-sm text-gray-900">
                        <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span><strong>Everything in Free</strong></span>
                      </li>
                      <li className="flex items-start gap-2 text-sm text-gray-900">
                        <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span><strong>Critical signals (85%+)</strong> with full details</span>
                      </li>
                      <li className="flex items-start gap-2 text-sm text-gray-900">
                        <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span><strong>Telegram alerts</strong> for hot opportunities</span>
                      </li>
                      <li className="flex items-start gap-2 text-sm text-gray-900">
                        <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span><strong>Tech stack analysis</strong> (50+ technologies)</span>
                      </li>
                      <li className="flex items-start gap-2 text-sm text-gray-900">
                        <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span><strong>CSV/JSON exports</strong> (unlimited)</span>
                      </li>
                      <li className="flex items-start gap-2 text-sm text-gray-900">
                        <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span><strong>REST API access</strong> (1000 req/day)</span>
                      </li>
                    </ul>

                    <button
                      onClick={handleUnlock}
                      className="w-full mt-6 px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-bold hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
                    >
                      <Unlock className="w-5 h-5" />
                      Unlock Premium Access
                    </button>

                    <p className="text-xs text-center text-gray-600 mt-3">
                      Cancel anytime • Secure payment via Stripe
                    </p>
                  </div>
                </div>

                {/* Features Grid */}
                <div className="border-t border-gray-200 pt-8">
                  <h3 className="text-xl font-bold text-gray-900 mb-6 text-center">
                    What You Get with Premium
                  </h3>
                  <div className="grid md:grid-cols-3 gap-6">
                    {features.map((feature, idx) => (
                      <div key={idx} className="flex items-start gap-3">
                        <div className="p-2 bg-blue-100 text-blue-600 rounded-lg flex-shrink-0">
                          {feature.icon}
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900 text-sm mb-1">
                            {feature.title}
                          </h4>
                          <p className="text-xs text-gray-600">{feature.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Trust Badges */}
                <div className="border-t border-gray-200 mt-8 pt-6 flex items-center justify-center gap-8 text-sm text-gray-600">
                  <div className="flex items-center gap-2">
                    <Shield className="w-4 h-4" />
                    <span>Secure Payments</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4" />
                    <span>Instant Access</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="w-4 h-4" />
                    <span>Cancel Anytime</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
