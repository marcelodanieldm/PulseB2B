"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface BlurredTextProps {
  children: React.ReactNode;
  isBlurred: boolean;
  className?: string;
}

export function BlurredText({ children, isBlurred, className }: BlurredTextProps) {
  return (
    <span
      className={cn(
        "relative inline-block transition-all duration-300",
        isBlurred && "select-none",
        className
      )}
    >
      {isBlurred && (
        <span
          className="absolute inset-0 backdrop-blur-md bg-gray-100/60 rounded"
          aria-hidden="true"
        />
      )}
      <span className={cn(isBlurred && "opacity-0")}>{children}</span>
      {isBlurred && (
        <span className="absolute inset-0 flex items-center justify-center text-gray-400 font-mono text-sm">
          •••••••
        </span>
      )}
    </span>
  );
}

interface BlurredAccessProps {
  children: React.ReactNode;
  isBlurred: boolean;
  onSignUp?: () => void;
  className?: string;
}

export function BlurredAccess({
  children,
  isBlurred,
  onSignUp,
  className,
}: BlurredAccessProps) {
  return (
    <div className={cn("relative", className)}>
      {isBlurred && (
        <div className="absolute inset-0 z-10 flex items-center justify-center backdrop-blur-sm bg-white/40 rounded-lg">
          <button
            onClick={onSignUp}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
          >
            Sign Up to View
          </button>
        </div>
      )}
      <div className={cn(isBlurred && "pointer-events-none")}>{children}</div>
    </div>
  );
}
