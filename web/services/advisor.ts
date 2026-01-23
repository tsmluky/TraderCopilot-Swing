
import { apiFetch } from "@/lib/api-client";

export const advisorService = {
    getProfile: async () => {
        return apiFetch("/advisor/profile");
    },

    updateProfile: async (payload: any) => {
        return apiFetch("/advisor/profile", {
            method: "PUT",
            body: JSON.stringify(payload)
        });
    },

    chat: async (messages: any[], context?: any) => {
        return apiFetch("/advisor/chat", {
            method: "POST",
            body: JSON.stringify({ messages, context })
        });
    },

    // Deterministic analyzer
    analyzePosition: async (payload: any) => {
        return apiFetch("/advisor/", {
            method: "POST",
            body: JSON.stringify(payload)
        });
    }
};
