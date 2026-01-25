"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode, useCallback } from "react";
import { apiFetch, AuthError } from "@/lib/api-client";
import { useRouter } from "next/navigation";

interface User {
    id: number;
    email: string;
    name: string;
    role: string;
    plan: string;
    allowed_tokens?: string[];
    plan_expires_at?: string | null;
    timezone?: string | null;
    telegram_chat_id?: string | null;
    telegram_username?: string | null;
    created_at: string;
}

type Entitlements = {
    tier?: string;
    plan_label?: string;
    expires_at?: string | null;
    allowed_tokens?: string[];
    allowed_timeframes?: string[];
    is_trial_expired?: boolean;
    telegram_access?: boolean;
    advisor_access?: boolean;
    features?: Record<string, any>;
};

interface AuthContextType {
    user: User | null;
    entitlements: Entitlements | null;
    token: string | null;
    isLoading: boolean;
    error: string | null;

    loginWithToken: (token: string) => Promise<void>;
    logout: () => void;
    refresh: () => Promise<void>;

    isLoggedIn: boolean;
    isTrialExpired: boolean;
    canAccessAdvisor: boolean;
    canAccessTelegram: boolean;
    allowedTokens: string[];
    allowedTimeframes: string[];
    canAccessTimeframe: (tf: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = "tc_token";
const TOKEN_COOKIE = "tc_token";

function getCookie(name: string): string | null {
    if (typeof document === "undefined") return null;
    const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const match = document.cookie.match(new RegExp(`(?:^|; )${escaped}=([^;]*)`));
    return match ? decodeURIComponent(match[1]) : null;
}

function setTokenCookie(token: string) {
    if (typeof document === "undefined") return;
    const maxAge = 60 * 60 * 24 * 7;
    const secure = typeof window !== "undefined" && window.location.protocol === "https:" ? "; Secure" : "";
    document.cookie = `${TOKEN_COOKIE}=${encodeURIComponent(token)}; Path=/; Max-Age=${maxAge}; SameSite=Lax${secure}`;
}

function clearTokenCookie() {
    if (typeof document === "undefined") return;
    document.cookie = `${TOKEN_COOKIE}=; Path=/; Max-Age=0; SameSite=Lax`;
}

function pickBooleanEntitlement(ent: Entitlements | null, key: string): boolean {
    if (!ent) return false;

    const top = (ent as any)[key];
    if (typeof top === "boolean") return top;

    if (!ent.features) return false;

    const f = ent.features[key];
    if (typeof f === "boolean") return f;

    if (f && typeof f === "object") {
        if (typeof f.remaining === "number") return f.remaining > 0 || (typeof f.limit === "number" && f.limit > 0);
        if (typeof f.limit === "number") return f.limit > 0;
    }

    return false;
}

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [entitlements, setEntitlements] = useState<Entitlements | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const router = useRouter();

    const fetchUserData = useCallback(async () => {
        setIsLoading(true);
        setError(null);

        const isBillingSuccess =
            typeof window !== "undefined" &&
            new URLSearchParams(window.location.search).get("billing") === "success";

        try {
            const [userData, entData] = await Promise.all([
                apiFetch<User>("/auth/users/me"),
                apiFetch<Entitlements>("/auth/me/entitlements"),
            ]);

            // If trial expired but we just returned from Stripe,
            // attempt a billing sync before redirecting to /trial-expired.
            if (entData?.is_trial_expired && isBillingSuccess) {
                try {
                    await apiFetch("/billing/sync", { method: "POST" });

                    const [user2, ent2] = await Promise.all([
                        apiFetch<User>("/auth/users/me"),
                        apiFetch<Entitlements>("/auth/me/entitlements"),
                    ]);

                    setUser(user2);
                    setEntitlements(ent2);

                    if (ent2?.is_trial_expired) {
                        router.push("/trial-expired");
                    } else {
                        // remove query param to avoid looping sync
                        router.replace("/dashboard");
                    }
                } catch (e) {
                    // If sync fails, fallback to original behavior
                    setUser(userData);
                    setEntitlements(entData);
                    router.push("/trial-expired");
                }
                return;
            }

            setUser(userData);
            setEntitlements(entData);

            if (entData?.is_trial_expired) {
                router.push("/trial-expired");
            }
        } catch (err: any) {
            if (err instanceof AuthError) {
                if (typeof window !== "undefined") localStorage.removeItem(TOKEN_KEY);
                clearTokenCookie();
                setToken(null);
                setUser(null);
                setEntitlements(null);
                router.push("/auth/login");
            } else {
                console.error("Auth Load Error:", err);
                setError(err?.message || "Failed to load user profile");
            }
        } finally {
            setIsLoading(false);
        }
    }, [router]);

    useEffect(() => {
        const storedToken =
            (typeof window !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null) ||
            getCookie(TOKEN_COOKIE);

        if (storedToken) {
            if (typeof window !== "undefined") localStorage.setItem(TOKEN_KEY, storedToken);
            setToken(storedToken);
            fetchUserData();
        } else {
            setIsLoading(false);
        }
    }, [fetchUserData]);

    const loginWithToken = async (newToken: string) => {
        if (typeof window !== "undefined") localStorage.setItem(TOKEN_KEY, newToken);
        setTokenCookie(newToken);
        setToken(newToken);
        await fetchUserData();
        router.push("/dashboard");
    };

    const logout = () => {
        if (typeof window !== "undefined") localStorage.removeItem(TOKEN_KEY);
        clearTokenCookie();
        setToken(null);
        setUser(null);
        setEntitlements(null);
        router.push("/auth/login");
    };

    const refresh = async () => {
        if (!token) return;
        await fetchUserData();
    };

    const canAccessAdvisor = pickBooleanEntitlement(entitlements, "advisor_access");
    const canAccessTelegram = pickBooleanEntitlement(entitlements, "telegram_access");
    const isTrialExpired = entitlements?.is_trial_expired ?? false;

    const allowedTokens = entitlements?.allowed_tokens ?? user?.allowed_tokens ?? [];
    const allowedTimeframes = entitlements?.allowed_timeframes ?? [];

    return (
        <AuthContext.Provider
            value={{
                user,
                entitlements,
                token,
                isLoading,
                error,
                loginWithToken,
                logout,
                refresh,
                isLoggedIn: !!user,
                isTrialExpired,
                canAccessAdvisor,
                canAccessTelegram,
                allowedTokens,
                allowedTimeframes,
                canAccessTimeframe: (tf: string) => allowedTimeframes.includes(tf),
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) throw new Error("useAuth must be used within an AuthProvider");
    return context;
}