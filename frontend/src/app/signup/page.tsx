'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { LoginModal } from '@/components/auth/LoginModal';
import { useAuth } from '@/hooks/useAuth';
import { motion } from 'framer-motion';
import { 
  Sparkles, 
  Mail,
  Phone,
  DollarSign, 
  BarChart3,
  Lock,
  Unlock,
  CheckCircle,
  Crown,
  Zap,
  Globe,
  TrendingUp,
  Shield,
  Clock,
  CreditCard
} from 'lucide-react';

/**
 * Signup Page
 * 
 * Hero page emphasizing FOMO and value proposition
 * Shows free vs premium features comparison
 * Opens LoginModal in signup mode
 */

export default function SignupPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const [showSignupModal, setShowSignupModal] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/continental');
    }
  }, [isAuthenticated, isLoading, router]);

  // Auto-open modal on mount
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      // Delay to let user see the value proposition
      const timer = setTimeout(() => {
        setShowSignupModal(true);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [isLoading, isAuthenticated]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0A0E1A] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0A0E1A] relative overflow-hidden">
      {/* Background gradient effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-purple-500/5 to-pink-500/5"></div>
      <div className="absolute top-0 left-1/3 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-0 right-1/3 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>

      <div className="relative z-10 container mx-auto px-6 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30 rounded-full mb-6">
            <Crown className="w-4 h-4 text-amber-400" />
            <span className="text-sm text-amber-400 font-medium">Start Free, Upgrade to Premium</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
            Unlock
            <span className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-transparent bg-clip-text"> Global Leads</span>
          </h1>
          
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            We show you WHO is hiring and WHY they're desperate...
            <br />
            <span className="text-white font-semibold">
              Premium unlocks direct contact to REACH them.
            </span>
          </p>

          <button
            onClick={() => setShowSignupModal(true)}
            className="px-10 py-5 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white text-lg font-bold rounded-xl shadow-2xl hover:shadow-3xl hover:scale-105 transform transition-all inline-flex items-center gap-3"
          >
            <Sparkles className="w-6 h-6" />
            Start Free Trial
            <span className="text-sm font-normal opacity-90">No credit card required</span>
          </button>
        </motion.div>

        {/* Free vs Premium comparison */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="max-w-6xl mx-auto mb-16"
        >
          <div className="grid md:grid-cols-2 gap-8">
            {/* Free Tier */}
            <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-8">
              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold text-white mb-2">Free Access</h3>
                <p className="text-gray-400 text-sm">See the opportunity, not the contact</p>
                <div className="mt-4 text-4xl font-bold text-white">$0</div>
                <p className="text-gray-500 text-sm">Forever free</p>
              </div>

              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-medium flex items-center gap-2">
                      Company Intelligence
                      <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded">VISIBLE</span>
                    </h4>
                    <p className="text-sm text-gray-400">
                      "TechCorp raised $10M, actively hiring React developers in SF. 🔥 URGENT"
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-medium flex items-center gap-2">
                      Tech Stack
                      <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded">VISIBLE</span>
                    </h4>
                    <p className="text-sm text-gray-400">React, Node.js, AWS, PostgreSQL</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-medium flex items-center gap-2">
                      Hiring Probability
                      <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded">VISIBLE</span>
                    </h4>
                    <p className="text-sm text-gray-400">87/100 - Actively recruiting</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-medium flex items-center gap-2">
                      Funding Range
                      <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded">VISIBLE</span>
                    </h4>
                    <p className="text-sm text-gray-400">$10M - $50M (approximate)</p>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-800">
                  <div className="flex items-start gap-3 opacity-50">
                    <Lock className="w-5 h-5 text-gray-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <h4 className="text-gray-600 font-medium flex items-center gap-2">
                        Contact Email
                        <span className="px-2 py-0.5 bg-gray-800 text-gray-600 text-xs rounded">BLURRED</span>
                      </h4>
                      <p className="text-sm text-gray-600 blur-sm select-none">hiring@techcorp.com</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 opacity-50 mt-4">
                    <Lock className="w-5 h-5 text-gray-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <h4 className="text-gray-600 font-medium flex items-center gap-2">
                        Direct Phone
                        <span className="px-2 py-0.5 bg-gray-800 text-gray-600 text-xs rounded">BLURRED</span>
                      </h4>
                      <p className="text-sm text-gray-600 blur-sm select-none">+1 (415) 555-0123</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 opacity-50 mt-4">
                    <Lock className="w-5 h-5 text-gray-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <h4 className="text-gray-600 font-medium flex items-center gap-2">
                        Exact Funding
                        <span className="px-2 py-0.5 bg-gray-800 text-gray-600 text-xs rounded">BLURRED</span>
                      </h4>
                      <p className="text-sm text-gray-600 blur-sm select-none">$15,234,567</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Premium Tier */}
            <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border-2 border-blue-500/50 rounded-2xl p-8 relative overflow-hidden">
              {/* Premium badge */}
              <div className="absolute top-0 right-0 bg-gradient-to-r from-amber-500 to-orange-500 px-4 py-2 rounded-bl-2xl">
                <Crown className="w-4 h-4 text-white inline mr-1" />
                <span className="text-white text-xs font-bold">PREMIUM</span>
              </div>

              <div className="text-center mb-6 mt-8">
                <h3 className="text-2xl font-bold text-white mb-2">Premium Access</h3>
                <p className="text-gray-300 text-sm">Direct contact info + everything free</p>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-white">$49</span>
                  <span className="text-gray-400">/month</span>
                </div>
                <p className="text-gray-500 text-sm mt-1">Cancel anytime • 7-day money-back</p>
              </div>

              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <Unlock className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-medium flex items-center gap-2">
                      <Mail className="w-4 h-4" />
                      Contact Emails
                      <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-xs rounded">UNLOCKED</span>
                    </h4>
                    <p className="text-sm text-blue-300">
                      hiring@techcorp.com • Direct decision maker contacts
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Unlock className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-medium flex items-center gap-2">
                      <Phone className="w-4 h-4" />
                      Direct Phone Numbers
                      <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-xs rounded">UNLOCKED</span>
                    </h4>
                    <p className="text-sm text-blue-300">
                      +1 (415) 555-0123 • Skip cold outreach
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Unlock className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="text-white font-medium flex items-center gap-2">
                      <DollarSign className="w-4 h-4" />
                      Exact Funding Amounts
                      <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-xs rounded">UNLOCKED</span>
                    </h4>
                    <p className="text-sm text-blue-300">
                      $15,234,567 • Precise valuation data
                    </p>
                  </div>
                </div>

                <div className="pt-4 border-t border-blue-500/30">
                  <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-amber-400" />
                    Everything in Free, plus:
                  </h4>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2 text-gray-300">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      Unlimited exports (CSV, JSON)
                    </div>
                    <div className="flex items-center gap-2 text-gray-300">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      Priority email alerts
                    </div>
                    <div className="flex items-center gap-2 text-gray-300">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      Advanced filtering
                    </div>
                    <div className="flex items-center gap-2 text-gray-300">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      API access (coming soon)
                    </div>
                  </div>
                </div>
              </div>

              <button
                onClick={() => setShowSignupModal(true)}
                className="w-full mt-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold rounded-xl shadow-lg hover:shadow-xl hover:scale-105 transform transition-all flex items-center justify-center gap-2"
              >
                <Crown className="w-5 h-5" />
                Upgrade to Premium
              </button>
            </div>
          </div>
        </motion.div>

        {/* Social proof */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="max-w-4xl mx-auto mb-16"
        >
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-8">
            <div className="text-center mb-8">
              <h3 className="text-2xl font-bold text-white mb-2">Trusted by 500+ Teams</h3>
              <p className="text-gray-400">Join recruiters and agencies closing deals faster</p>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <BarChart3 className="w-8 h-8 text-blue-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">3.5x</div>
                <div className="text-sm text-gray-400">Faster lead qualification</div>
              </div>
              <div className="text-center">
                <TrendingUp className="w-8 h-8 text-green-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">$127K</div>
                <div className="text-sm text-gray-400">Avg. revenue per user</div>
              </div>
              <div className="text-center">
                <Globe className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-white">19</div>
                <div className="text-sm text-gray-400">Countries monitored</div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* CTA section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to close more deals?
          </h2>
          <p className="text-gray-400 mb-6">
            Start with free access. Upgrade anytime to unlock contact info.
          </p>
          
          <button
            onClick={() => setShowSignupModal(true)}
            className="px-10 py-5 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white text-lg font-bold rounded-xl shadow-2xl hover:shadow-3xl hover:scale-105 transform transition-all inline-flex items-center gap-3"
          >
            Create Free Account
          </button>

          <p className="mt-4 text-sm text-gray-500">
            Already have an account?{' '}
            <a href="/login" className="text-blue-400 hover:text-blue-300 font-medium">
              Sign in
            </a>
          </p>
        </motion.div>

        {/* Trust badges */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="flex flex-wrap items-center justify-center gap-8 text-sm text-gray-500"
        >
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4" />
            <span>SSL encrypted</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            <span>Cancel anytime</span>
          </div>
          <div className="flex items-center gap-2">
            <CreditCard className="w-4 h-4" />
            <span>7-day money-back</span>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4" />
            <span>Instant activation</span>
          </div>
        </motion.div>
      </div>

      {/* Signup Modal */}
      <LoginModal
        isOpen={showSignupModal}
        onClose={() => setShowSignupModal(false)}
        redirectTo="/continental"
      />
    </div>
  );
}
