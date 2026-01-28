import { apiFetch } from "@/lib/api-client";
import { Signal } from "@/lib/types";

export const signalsService = {
    getRecent: async (limit = 50, offset = 0) => {
        return apiFetch(`/signals/?limit=${limit}&offset=${offset}`);
    },

    getById: async (id: string) => {
        return apiFetch(`/signals/${id}`);
    },

    createManual: async (data: any) => {
        return apiFetch("/signals/", {
            method: "POST",
            body: JSON.stringify(data)
        });
    },

    acceptSignal: async (id: string) => {
        return apiFetch(`/signals/${id}/accept`, {
            method: "POST"
        });
    },

    deleteSignal: async (id: string) => {
        return apiFetch(`/signals/${id}`, {
            method: "DELETE"
        });
    }
};
