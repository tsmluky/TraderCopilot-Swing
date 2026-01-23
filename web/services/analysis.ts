
import { apiFetch } from "@/lib/api-client";

interface AnalyzeParams {
    token: string;
    timeframe: string;
    message?: string;
    user_message?: string;
    language?: string;
}

export const analysisService = {
    analyzeLite: async (params: AnalyzeParams) => {
        return apiFetch("/analysis/lite", {
            method: "POST",
            body: JSON.stringify({
                token: params.token,
                timeframe: params.timeframe,
                mode: "LITE",
                message: params.message
            })
        });
    },

    analyzePro: async (params: AnalyzeParams) => {
        return apiFetch("/analysis/pro", {
            method: "POST",
            body: JSON.stringify({
                token: params.token,
                timeframe: params.timeframe,
                user_message: params.user_message,
                language: params.language || 'es'
            }),
            timeoutMs: 90000 // 90s for extensive RAG + LLM generation
        });
    }
};
