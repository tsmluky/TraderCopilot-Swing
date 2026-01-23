
import { apiFetch } from "@/lib/api-client";

interface LogsParams {
    mode?: string;
    saved_only?: boolean;
    include_system?: boolean;
    page?: number;
    limit?: number;
    token?: string;
}

export const logsService = {
    getRecentLogs: async (params: LogsParams) => {
        // Flatten params for query string
        const qParams: Record<string, any> = { ...params };
        return apiFetch("/logs/recent", { params: qParams });
    },

    getLogsByToken: async (token: string, mode: string = "ALL", limit: number = 50) => {
        // Using path param based on Prompt: /logs/{mode}/{token}
        return apiFetch(`/logs/${mode}/${token}`, {
            params: { limit }
        });
    },

    trackSignal: async (signal_id: string | number) => {
        // Assuming body contains signal_id or it's a path? Prompt says POST /logs/track
        return apiFetch("/logs/track", {
            method: "POST",
            body: JSON.stringify({ signal_id })
        });
    },

    toggleSave: async (signal_id: string | number) => {
        return apiFetch(`/logs/${signal_id}/toggle_save`, {
            method: "POST"
        });
    }
};
