/**
 * =====================================================
 * TOAST NOTIFICATION COMPONENT
 * =====================================================
 * Purpose: Show welcome messages and notifications
 * Author: Senior Frontend Developer
 * Date: December 22, 2025
 * =====================================================
 */

'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export interface Toast {
  id: string;
  type: 'success' | 'info' | 'warning' | 'error';
  message: string;
  duration?: number;
  icon?: string;
}

let toastId = 0;
const toastListeners: Array<(toast: Toast) => void> = [];

/**
 * Show a toast notification
 */
export function showToast(
  message: string,
  type: Toast['type'] = 'info',
  duration = 5000,
  icon?: string
) {
  const toast: Toast = {
    id: `toast-${toastId++}`,
    type,
    message,
    duration,
    icon,
  };

  toastListeners.forEach((listener) => listener(toast));
  return toast.id;
}

/**
 * Toast container component
 */
export function ToastContainer() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    const listener = (toast: Toast) => {
      setToasts((prev) => [...prev, toast]);

      // Auto-remove after duration
      if (toast.duration && toast.duration > 0) {
        setTimeout(() => {
          setToasts((prev) => prev.filter((t) => t.id !== toast.id));
        }, toast.duration);
      }
    };

    toastListeners.push(listener);

    return () => {
      const index = toastListeners.indexOf(listener);
      if (index > -1) toastListeners.splice(index, 1);
    };
  }, []);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 pointer-events-none">
      <AnimatePresence>
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
        ))}
      </AnimatePresence>
    </div>
  );
}

/**
 * Individual toast item
 */
function ToastItem({ toast, onClose }: { toast: Toast; onClose: () => void }) {
  const bgColors = {
    success: 'bg-green-500',
    info: 'bg-blue-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500',
  };

  const icons = {
    success: '✓',
    info: 'ℹ',
    warning: '⚠',
    error: '✕',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, x: 100 }}
      animate={{ opacity: 1, y: 0, x: 0 }}
      exit={{ opacity: 0, x: 100 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="pointer-events-auto"
    >
      <div
        className={`
          ${bgColors[toast.type]} 
          text-white 
          px-6 py-4 
          rounded-lg 
          shadow-2xl 
          flex items-center gap-3
          min-w-[300px] max-w-[400px]
          backdrop-blur-sm
        `}
      >
        <span className="text-2xl flex-shrink-0">
          {toast.icon || icons[toast.type]}
        </span>
        <p className="flex-1 text-sm font-medium">{toast.message}</p>
        <button
          onClick={onClose}
          className="flex-shrink-0 hover:bg-white/20 rounded p-1 transition-colors"
          aria-label="Close"
        >
          ✕
        </button>
      </div>
    </motion.div>
  );
}

/**
 * Telegram Welcome Toast (special styling)
 */
export function showTelegramWelcome(campaign?: string) {
  const messages = {
    daily_signal: "🤖 Welcome Telegram Member! Here's your Daily Signal.",
    latest_command: "🤖 Welcome! Thanks for using /latest command.",
    unknown: "🤖 Welcome Telegram Member! Explore high-value leads.",
  };

  const message = messages[campaign as keyof typeof messages] || messages.unknown;

  return showToast(message, 'info', 6000, '🤖');
}
