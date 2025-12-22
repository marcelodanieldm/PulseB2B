/**
 * =====================================================
 * TELEGRAM CTA COMPONENT
 * =====================================================
 * Purpose: Enhanced CTA for high-intent Telegram users
 * Author: Senior Frontend Developer
 * Date: December 22, 2025
 * =====================================================
 */

'use client';

import { motion } from 'framer-motion';
import { useTelegramReferral } from '@/hooks/useTelegramReferral';

interface TelegramCTAProps {
  onClick: () => void;
  isPremium: boolean;
  className?: string;
}

/**
 * Enhanced "Unlock Details" CTA for Telegram users
 * More prominent, with urgency indicators
 */
export function TelegramCTA({ onClick, isPremium, className = '' }: TelegramCTAProps) {
  const { isTelegramUser, trackConversion } = useTelegramReferral();

  if (isPremium) return null; // No CTA needed for premium users

  const handleClick = () => {
    if (isTelegramUser) {
      trackConversion('view_details');
    }
    onClick();
  };

  // Standard CTA for non-Telegram users
  if (!isTelegramUser) {
    return (
      <button
        onClick={handleClick}
        className={`
          px-4 py-2 
          bg-gradient-to-r from-purple-600 to-pink-600 
          text-white text-sm font-semibold 
          rounded-lg 
          hover:from-purple-700 hover:to-pink-700 
          transition-all duration-200
          ${className}
        `}
      >
        🔓 Unlock Details
      </button>
    );
  }

  // Enhanced CTA for Telegram users (high intent)
  return (
    <motion.button
      onClick={handleClick}
      className={`
        relative
        px-6 py-3 
        bg-gradient-to-r from-purple-600 via-pink-600 to-red-600 
        text-white text-base font-bold 
        rounded-xl 
        hover:from-purple-700 hover:via-pink-700 hover:to-red-700 
        transition-all duration-200
        shadow-2xl hover:shadow-purple-500/50
        overflow-hidden
        ${className}
      `}
      animate={{
        boxShadow: [
          '0 20px 40px rgba(168, 85, 247, 0.4)',
          '0 20px 40px rgba(236, 72, 153, 0.4)',
          '0 20px 40px rgba(220, 38, 38, 0.4)',
          '0 20px 40px rgba(168, 85, 247, 0.4)',
        ],
      }}
      transition={{
        duration: 3,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    >
      {/* Shimmer effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
        animate={{
          x: ['-100%', '200%'],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'linear',
        }}
      />

      {/* Content */}
      <span className="relative flex items-center gap-2">
        <span className="text-xl">🚀</span>
        <span>Unlock Full Details</span>
        <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">
          Premium
        </span>
      </span>

      {/* Urgency indicator */}
      <motion.div
        className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"
        animate={{
          scale: [1, 1.2, 1],
          opacity: [1, 0.7, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
        }}
      />
    </motion.button>
  );
}

/**
 * Sticky mobile CTA for Telegram users
 * Floats at bottom of screen on mobile
 */
export function TelegramStickyMobileCTA({ onClick, isPremium }: TelegramCTAProps) {
  const { isTelegramUser, trackConversion } = useTelegramReferral();

  if (!isTelegramUser || isPremium) return null;

  const handleClick = () => {
    trackConversion('view_details');
    onClick();
  };

  return (
    <motion.div
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      className="fixed bottom-0 left-0 right-0 z-40 p-4 bg-gradient-to-t from-black via-black/95 to-transparent backdrop-blur-sm md:hidden"
    >
      <button
        onClick={handleClick}
        className="
          w-full
          px-6 py-4
          bg-gradient-to-r from-purple-600 via-pink-600 to-red-600
          text-white text-lg font-bold
          rounded-xl
          shadow-2xl
          flex items-center justify-center gap-3
          active:scale-95
          transition-transform
        "
      >
        <span className="text-2xl">🚀</span>
        <span>Unlock Contact Details</span>
        <span className="text-sm bg-white/20 px-3 py-1 rounded-full">
          $49/mo
        </span>
      </button>

      {/* Value props */}
      <p className="text-center text-xs text-gray-400 mt-2">
        💎 Instant access • 🔥 Email & Phone • 💰 Exact funding
      </p>
    </motion.div>
  );
}

/**
 * Telegram conversion banner (shows above table)
 */
export function TelegramConversionBanner({ onUpgrade }: { onUpgrade: () => void }) {
  const { isTelegramUser, campaign, trackConversion } = useTelegramReferral();

  if (!isTelegramUser) return null;

  const handleClick = () => {
    trackConversion('premium');
    onUpgrade();
  };

  const campaignMessages = {
    daily_signal: "You're viewing today's hottest lead from our Daily Signal!",
    latest_command: "Great timing! This lead has a 90%+ hiring probability.",
    unknown: "Welcome from Telegram! You're viewing high-value B2B leads.",
  };

  const message = campaignMessages[campaign as keyof typeof campaignMessages] || campaignMessages.unknown;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-6 p-4 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-xl backdrop-blur-sm"
    >
      <div className="flex items-start gap-4">
        <span className="text-3xl">🤖</span>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-white mb-1">
            Welcome Telegram Member!
          </h3>
          <p className="text-sm text-gray-300 mb-3">
            {message}
          </p>
          <button
            onClick={handleClick}
            className="
              px-4 py-2
              bg-gradient-to-r from-purple-600 to-pink-600
              text-white text-sm font-semibold
              rounded-lg
              hover:from-purple-700 hover:to-pink-700
              transition-all duration-200
              inline-flex items-center gap-2
            "
          >
            <span>🔓</span>
            <span>Unlock Contact Info</span>
            <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">
              $49/mo
            </span>
          </button>
          <p className="text-xs text-gray-400 mt-2">
            ✓ Email & Phone • ✓ Exact Funding • ✓ Cancel Anytime
          </p>
        </div>
      </div>
    </motion.div>
  );
}
