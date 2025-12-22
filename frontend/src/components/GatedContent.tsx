/**
 * Gated Content Component
 * Applies blur and lock overlay for non-premium users
 */

'use client';

import React from 'react';
import { Lock } from 'lucide-react';
import { cn } from '@/lib/cn';
import { Button } from '@/components/ui/button';

interface GatedContentProps {
  children: React.ReactNode;
  isLocked: boolean;
  onUnlock: () => void;
  className?: string;
  showButton?: boolean;
  buttonText?: string;
  contentType?: 'email' | 'phone' | 'funding' | 'generic';
}

export function GatedContent({
  children,
  isLocked,
  onUnlock,
  className,
  showButton = true,
  buttonText = 'Unlock Now',
  contentType = 'generic',
}: GatedContentProps) {
  if (!isLocked) {
    return <>{children}</>;
  }

  return (
    <div className={cn('relative inline-block', className)}>
      {/* Blurred content */}
      <div className="blur-sm pointer-events-none select-none">
        {children}
      </div>

      {/* Lock overlay */}
      {showButton && (
        <div className="absolute inset-0 flex items-center justify-center">
          <Button
            onClick={onUnlock}
            size="sm"
            variant="default"
            className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white shadow-lg hover:shadow-xl transition-all duration-200 gap-2 pointer-events-auto"
          >
            <Lock className="w-3 h-3" />
            {buttonText}
          </Button>
        </div>
      )}
    </div>
  );
}

/**
 * Gated Table Cell - For use in table columns
 */
interface GatedTableCellProps {
  value: React.ReactNode;
  isLocked: boolean;
  onUnlock: () => void;
  placeholder?: string;
}

export function GatedTableCell({
  value,
  isLocked,
  onUnlock,
  placeholder = '•••••',
}: GatedTableCellProps) {
  if (!isLocked) {
    return <>{value}</>;
  }

  return (
    <div className="relative group">
      {/* Blurred placeholder */}
      <div className="blur-sm pointer-events-none select-none text-muted-foreground">
        {placeholder}
      </div>

      {/* Hover overlay with unlock button */}
      <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-background/80 backdrop-blur-sm">
        <Button
          onClick={onUnlock}
          size="sm"
          variant="ghost"
          className="h-7 text-xs gap-1.5 hover:bg-amber-500/20 hover:text-amber-500 border border-amber-500/30"
        >
          <Lock className="w-3 h-3" />
          Unlock
        </Button>
      </div>
    </div>
  );
}

/**
 * Gated Inline - For inline text with lock icon
 */
interface GatedInlineProps {
  value: string | React.ReactNode;
  isLocked: boolean;
  onUnlock: () => void;
  showIcon?: boolean;
}

export function GatedInline({
  value,
  isLocked,
  onUnlock,
  showIcon = true,
}: GatedInlineProps) {
  if (!isLocked) {
    return <>{value}</>;
  }

  return (
    <button
      onClick={onUnlock}
      className="inline-flex items-center gap-1.5 text-muted-foreground hover:text-amber-500 transition-colors cursor-pointer group"
    >
      <span className="blur-sm pointer-events-none select-none">•••••</span>
      {showIcon && (
        <Lock className="w-3 h-3 text-amber-500 group-hover:scale-110 transition-transform" />
      )}
    </button>
  );
}
