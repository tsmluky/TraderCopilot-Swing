import { apiFetch } from "@/lib/api-client";

export const billingService = {
  createCheckoutSession: async (plan: "TRADER" | "PRO") => {
    return apiFetch<{ url: string }>("/billing/checkout-session", {
      method: "POST",
      body: JSON.stringify({ plan }),
    });
  },

  createPortalSession: async () => {
    return apiFetch<{ url: string }>("/billing/portal-session", {
      method: "POST",
    });
  },
};