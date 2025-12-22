'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import confetti from 'canvas-confetti';
import { usePremiumStatus } from '@/hooks/usePremiumStatus';

/**
 * Success Page
 * 
 * Shown after successful Stripe payment
 * Features:
 *   - Confetti celebration effect
 *   - "Refreshing your data..." message
 *   - Polls for premium status update (Stripe webhook processing)
 *   - Redirects to dashboard when premium is active
 * 
 * Route: /success
 * 
 * Stripe Setup:
 *   - Set success_url in Payment Link to: https://yourdomain.com/success
 *   - Webhook will update is_premium in users table
 */

export default function SuccessPage() {
  const router = useRouter();
  const { isPremium, refreshStatus } = usePremiumStatus();
  const [pollingCount, setPollingCount] = useState(0);
  const [statusMessage, setStatusMessage] = useState('Processing your payment...');

  // Trigger confetti on mount
  useEffect(() => {
    // Initial confetti burst
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#3B82F6', '#8B5CF6', '#EC4899'],
    });

    // Continuous confetti for 3 seconds
    const interval = setInterval(() => {
      confetti({
        particleCount: 50,
        angle: 60,
        spread: 55,
        origin: { x: 0, y: 0.6 },
        colors: ['#3B82F6', '#8B5CF6'],
      });
      confetti({
        particleCount: 50,
        angle: 120,
        spread: 55,
        origin: { x: 1, y: 0.6 },
        colors: ['#8B5CF6', '#EC4899'],
      });
    }, 400);

    setTimeout(() => clearInterval(interval), 3000);

    return () => clearInterval(interval);
  }, []);

  // Poll for premium status update
  useEffect(() => {
    if (isPremium) {
      // Premium activated! Redirect to dashboard
      setStatusMessage('Premium activated! Redirecting...');
      setTimeout(() => {
        router.push('/continental?premium=activated');
      }, 2000);
      return;
    }

    // Poll every 2 seconds for premium status (max 30 attempts = 60 seconds)
    const pollInterval = setInterval(async () => {
      setPollingCount(prev => {
        const newCount = prev + 1;
        
        if (newCount > 30) {
          // Timeout after 60 seconds
          setStatusMessage('Taking longer than expected. Check your email for confirmation.');
          clearInterval(pollInterval);
          return newCount;
        }

        if (newCount > 5) {
          setStatusMessage('Almost there... Processing your subscription');
        } else {
          setStatusMessage('Refreshing your data...');
        }

        return newCount;
      });

      await refreshStatus();
    }, 2000);

    return () => clearInterval(pollInterval);
  }, [isPremium, refreshStatus, router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Success Card */}
        <div className="bg-white rounded-2xl shadow-2xl p-8 md:p-12 text-center space-y-8">
          {/* Success Icon */}
          <div className="relative">
            <div className="mx-auto w-24 h-24 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center animate-bounce-slow">
              <svg 
                className="w-12 h-12 text-white" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={3} 
                  d="M5 13l4 4L19 7" 
                />
              </svg>
            </div>
            {/* Pulse effect */}
            <div className="absolute inset-0 mx-auto w-24 h-24 bg-green-400 rounded-full animate-ping opacity-20"></div>
          </div>

          {/* Title */}
          <div>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Welcome to Premium! 🎉
            </h1>
            <p className="text-xl text-gray-600">
              Your payment was successful
            </p>
          </div>

          {/* Status Message */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
            <div className="flex items-center justify-center space-x-3">
              {/* Loading Spinner */}
              <div className="w-5 h-5 border-3 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-lg font-medium text-blue-900">
                {statusMessage}
              </p>
            </div>
          </div>

          {/* What's Unlocked */}
          <div className="border-t border-gray-200 pt-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              What's Now Unlocked
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              <UnlockedFeature 
                icon="📧"
                title="Direct Email Contacts"
                description="Access verified emails for every lead"
              />
              <UnlockedFeature 
                icon="📞"
                title="Phone Numbers"
                description="Call decision-makers immediately"
              />
              <UnlockedFeature 
                icon="💰"
                title="Exact Funding Amounts"
                description="See precise funding data and dates"
              />
              <UnlockedFeature 
                icon="📊"
                title="Unlimited Exports"
                description="Export data in CSV and JSON formats"
              />
            </div>
          </div>

          {/* Manual Refresh Button (if polling takes too long) */}
          {pollingCount > 15 && (
            <div className="pt-4">
              <button
                onClick={async () => {
                  await refreshStatus();
                  if (isPremium) {
                    router.push('/continental?premium=activated');
                  }
                }}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl hover:scale-105 transform transition-all"
              >
                Refresh Status Manually
              </button>
              <p className="mt-3 text-sm text-gray-500">
                If premium isn't activating, try refreshing or{' '}
                <a href="/continental" className="text-blue-600 hover:underline">
                  return to dashboard
                </a>
              </p>
            </div>
          )}

          {/* Support */}
          <div className="text-sm text-gray-500 pt-4 border-t border-gray-100">
            Questions? Contact{' '}
            <a href="mailto:support@pulseb2b.com" className="text-blue-600 hover:underline font-medium">
              support@pulseb2b.com
            </a>
          </div>
        </div>

        {/* Subtle hint */}
        <p className="text-center mt-6 text-gray-500">
          Check your email for receipt and account details
        </p>
      </div>
    </div>
  );
}

/**
 * UnlockedFeature Component
 */
interface UnlockedFeatureProps {
  icon: string;
  title: string;
  description: string;
}

function UnlockedFeature({ icon, title, description }: UnlockedFeatureProps) {
  return (
    <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-4 text-left">
      <div className="text-3xl mb-2">{icon}</div>
      <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}

// CSS for custom animations (add to globals.css if not already present)
// @keyframes bounce-slow {
//   0%, 100% { transform: translateY(0); }
//   50% { transform: translateY(-10px); }
// }
// .animate-bounce-slow {
//   animation: bounce-slow 2s infinite;
// }
