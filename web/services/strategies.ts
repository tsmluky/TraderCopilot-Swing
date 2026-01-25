import { apiFetch } from "@/lib/api-client";
import type { Strategy } from "@/lib/types";

// Update return type to allow ANY because new backend returns { offerings: ..., locked_offerings: ... }
// and the component handles it.
// The component expects: { offerings: StrategyOffering[], locked_offerings: StrategyOffering[] }
// But we can also keep "Strategy[]" in the signature if we just return "any" for now to unblock.
// Better: return Promise<any> to signal structure change.

export const strategiesService = {
  getMarketplace: async (): Promise<any> => {
    // RAW FETCH - Let the page component handle the structure
    // Backend returns: { offerings: [...], locked_offerings: [...] }
    return apiFetch("/strategies/marketplace");
  },

  createPersona: async (payload: any) => {
    // Deprecated backend-side, but keep for interface compat
    return apiFetch("/strategies/marketplace/create", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  togglePersona: async (personaId: string): Promise<{ status?: string; enabled?: boolean }> => {
    // Deprecated
    return apiFetch(`/strategies/marketplace/${personaId}/toggle`, {
      method: "PATCH",
    });
  },

  deletePersona: async (personaId: string) => {
    // Deprecated
    return apiFetch(`/strategies/marketplace/${personaId}`, {
      method: "DELETE",
    });
  },

  updatePersona: async (personaId: string, payload: { timeframe?: string; risk_profile?: string }) => {
    // Deprecated
    return apiFetch(`/strategies/marketplace/${personaId}/update`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  getHistory: async (personaId: string) => {
    return apiFetch(`/strategies/marketplace/${personaId}/history`);
  },
};