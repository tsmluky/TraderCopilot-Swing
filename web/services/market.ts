
import { apiFetch } from "@/lib/api-client";

export const marketService = {
    getMarketSummary: async (symbols?: string[]) => {
        // This endpoint wasn't in the dump explicitly, user said "GET /market/summary?symbols=..."
        // If it doesn't exist, we might need to fallback or it is yet to be implemented in backend.
        // For now, I implement the client call as requested.
        const params = symbols ? { symbols: symbols.join(",") } : undefined;
        return apiFetch("/market/summary", { params });
    },

    getOhlcv: async (token: string, timeframe: string = "4h", limit: number = 100) => {
        return apiFetch(`/market/ohlcv/${token}`, {
            params: { timeframe, limit }
        });
    }
};
