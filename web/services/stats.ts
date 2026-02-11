
import { apiFetch } from "@/lib/api-client";

export interface DashboardStats {
    summary: {
        win_rate_24h: number;
        signals_evaluated_24h: number;
        open_signals: number;
        pnl_7d: number;
        signals_evaluated_7d: number;  // Was missing in interface but present in usage
        wins_7d: number;
        losses_7d: number;
    };
    chart: Array<{ date: string; wins: number; losses: number }>;
}

export const statsService = {
    getDashboardStats: async (source: string = 'ALL') => {
        return apiFetch<DashboardStats>(`/stats/dashboard?source_filter=${source}`);
    },

    getStatsSummary: async () => {
        return apiFetch("/stats/summary");
    }
};
