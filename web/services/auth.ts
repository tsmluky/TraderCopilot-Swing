
import { apiFetch } from "@/lib/api-client";

export const authService = {
    // Login returns the raw token response
    login: async (email: string, password: string) => {
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        return apiFetch<{ access_token: string; user: any }>("/auth/token", {
            method: "POST",
            body: formData, // Automatic Content-Type handling in api-client
        });
    },

    register: async (payload: any) => {
        return apiFetch("/auth/register", {
            method: "POST",
            body: JSON.stringify(payload),
        });
    },

    updateTelegram: async (chatId: string) => {
        // NOTE: Based on user prompt, this uses PATCH /auth/users/me/telegram
        // But we should verify if backend has this specific path. 
        // The OpenAPI dump shows /notify/telegram and /telegram/webhook, but also PATCH /auth/users/me might exist or be generic.
        // Based on Prompt "Settings (cuenta)": PATCH /auth/users/me/telegram
        // Let's assume the user is right or we shim it.
        // Actually, checking standard CRUD, it might be PATCH /auth/users/me with { telegram_chat_id: ... }
        // I will trust the prompt for now, but fallback to generic update if needed.
        return apiFetch("/auth/users/me/telegram", {
            method: "PATCH",
            body: JSON.stringify({ chat_id: chatId })
        });
    },

    updatePassword: async (oldPassword: string, newPassword: string) => {
        return apiFetch("/auth/users/me/password", {
            method: "PATCH",
            body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
        });
    },

    updateTimezone: async (timezone: string) => {
        return apiFetch("/auth/users/me/timezone", {
            method: "PATCH",
            body: JSON.stringify({ timezone })
        });
    }
};
