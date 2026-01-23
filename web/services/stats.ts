
import { apiFetch } from "@/lib/api-client";

export interface DashboardStats {
    summary: {
        win_rate_24h: number;
        signals_evaluated_24h: number;
        open_signals: number;
        pnl_7d: number;
    };
    chart: Array<{ date: string; wins: number; losses: number }>;
}

export const statsService = {
    getDashboardStats: async () => {
        return apiFetch<DashboardStats>("/stats/dashboard");
    },

    getStatsSummary: async () => {
        return apiFetch("/stats/summary");
    }
};
