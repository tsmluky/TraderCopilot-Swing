"use client";

import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useAuth } from "@/context/auth-context";
import { type Plan, type Token, type Timeframe, type User } from "./types";

// Keep types compatible with old usage
type Entitlements = {
  tokens: Token[];
  timeframes: Timeframe[];
  features: {
    ai_analysis: { limit: number; used: number; remaining: number };
    advisor_chat: { limit: number; used: number; remaining: number };
  };
};

type UserContextType = {
  user: User | null;
  setUser: (user: User | null) => void;
  entitlements: Entitlements;
  setPlan: (plan: Plan) => void;
  isTrialExpired: boolean;
  canAccessToken: (token: Token) => boolean;
  canAccessTimeframe: (timeframe: Timeframe) => boolean;
  canAccessAdvisor: () => boolean;
  canAccessTelegram: () => boolean;

  authToken: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
};

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  // Pass-through since AuthProvider is valid at root
  return <>{children}</>;
}

export function useUser() {
  const {
    user: authUser,
    entitlements: authEntitlements, // Destructure entitlements
    token,
    logout,
    refresh,
    isTrialExpired,
    allowedTokens,
    allowedTimeframes,
    canAccessAdvisor,
    canAccessTelegram,
    canAccessTimeframe
  } = useAuth();

  // Map AuthUser to UI User
  const rawPlan = (authUser?.plan || 'FREE').toUpperCase();
  let normalizedPlan: Plan = 'FREE';

  if (rawPlan.includes('PRO') || rawPlan.includes('OWNER')) {
    normalizedPlan = 'PRO';
  } else if (rawPlan.includes('TRADER') || rawPlan.includes('BASIC')) {
    normalizedPlan = 'TRADER';
  }

  // Robust Date Parsing
  const rawExpiry = authEntitlements?.expires_at || authUser?.plan_expires_at;
  const expiryDate = rawExpiry ? new Date(rawExpiry) : undefined;

  const uiUser: User | null = authUser ? {
    id: String(authUser.id),
    email: authUser.email,
    name: authUser.name,
    plan: normalizedPlan,
    trialExpiresAt: (expiryDate && !isNaN(expiryDate.getTime())) ? expiryDate : undefined,
    telegramConnected: !!authUser.telegram_chat_id,
    telegram_chat_id: authUser.telegram_chat_id || undefined,
    telegram_username: authUser.telegram_username || undefined
  } : null;

  // Construct UI entitlements from AuthContext data
  const entitlements: Entitlements = {
    tokens: (allowedTokens as Token[]) || [],
    timeframes: (allowedTimeframes as Timeframe[]) || [],
    features: {
      ai_analysis: { limit: 999, used: 0, remaining: 999 }, // Mocked for UI compat
      advisor_chat: { limit: 999, used: 0, remaining: canAccessAdvisor ? 999 : 0 }
    }
  };

  return {
    user: uiUser,
    setUser: () => { }, // noop
    entitlements,
    setPlan: () => { }, // noop
    isTrialExpired,
    canAccessToken: (t: Token) => {
      if (normalizedPlan === 'PRO') return true;
      return allowedTokens.includes(t);
    },
    canAccessTimeframe: (tf: Timeframe) => {
      if (normalizedPlan === 'PRO') return true;
      return canAccessTimeframe(tf);
    },
    canAccessAdvisor: () => canAccessAdvisor,
    canAccessTelegram: () => canAccessTelegram,

    authToken: token,
    login: async () => console.warn("useUser.login is deprecated"),
    register: async () => console.warn("useUser.register is deprecated"),
    logout,
    refresh
  };
}
