import { apiFetch } from "@/lib/api-client";
import type { Strategy, Timeframe, Token } from "@/lib/types";

type MarketplacePersona = {
  id: string;
  name: string;
  description?: string;
  symbol?: string | string[];
  timeframe?: string | string[];
  tokens?: string[] | string;
  timeframes?: string[] | string;
  win_rate?: string | number;
  avg_return?: number | string;
  total_signals?: number;
  signals?: number;
  is_active?: boolean;
  enabled?: boolean | number;
};

function toTimeframeArray(input: unknown): Timeframe[] {
  const arr = Array.isArray(input) ? input : (input ? [input] : []);
  const norm = arr
    .map((x) => String(x).trim())
    .map((x) => x.toUpperCase())
    .map((x) => (x === "1H" || x === "1HR" || x === "1HOUR" || x === "1H " ? "1H" : x))
    .map((x) => (x === "4H" || x === "4HR" || x === "4HOUR" ? "4H" : x))
    .map((x) => (x === "1D" || x === "1DAY" || x === "D" ? "1D" : x))
    .filter((x) => x === "1H" || x === "4H" || x === "1D") as Timeframe[];

  // fallback default (no romper UI)
  return norm.length ? norm : (["4H"] as Timeframe[]);
}

function toTokenArray(input: unknown): Token[] {
  const arr = Array.isArray(input) ? input : (input ? [input] : []);
  const norm = arr
    .map((x) => String(x).trim().toUpperCase())
    .filter((x) => ["BTC", "ETH", "SOL", "BNB", "XRP"].includes(x)) as Token[];

  // fallback default
  return norm.length ? norm : (["BTC"] as Token[]);
}

function parseWinRate(input: unknown): number {
  if (typeof input === "number" && Number.isFinite(input)) return input;
  const s = String(input ?? "").trim();
  const m = s.match(/(\d+(\.\d+)?)/);
  if (!m) return 0;
  const v = Number(m[1]);
  return Number.isFinite(v) ? v : 0;
}

function parseNumber(input: unknown): number {
  if (typeof input === "number" && Number.isFinite(input)) return input;
  const s = String(input ?? "").trim();
  const m = s.match(/-?\d+(\.\d+)?/);
  if (!m) return 0;
  const v = Number(m[0]);
  return Number.isFinite(v) ? v : 0;
}

function parseEnabled(p: MarketplacePersona): boolean {
  if (typeof p.is_active === "boolean") return p.is_active;
  if (typeof p.enabled === "boolean") return p.enabled;
  if (typeof p.enabled === "number") return p.enabled === 1;
  return false;
}

function mapPersonaToStrategy(p: MarketplacePersona): Strategy {
  // Backend actual: symbol/timeframe (single) + is_active + win_rate "45%"
  // Frontend wants: tokens[] + timeframes[] + isActive + winRate number
  const timeframes = p.timeframes ?? p.timeframe;
  const tokens = p.tokens ?? p.symbol;

  return {
    id: p.id,
    name: p.name,
    description: p.description ?? "",
    winRate: parseWinRate(p.win_rate),
    avgReturn: parseNumber((p as any).avg_return),
    signals: typeof p.total_signals === "number" ? p.total_signals : (typeof p.signals === "number" ? p.signals : 0),
    timeframes: toTimeframeArray(timeframes),
    tokens: toTokenArray(tokens),
    isActive: parseEnabled(p),
  };
}

export const strategiesService = {
  getMarketplace: async (): Promise<Strategy[]> => {
    const raw = await apiFetch("/strategies/marketplace");

    const list: MarketplacePersona[] =
      Array.isArray(raw) ? raw :
        Array.isArray((raw as any)?.results) ? (raw as any).results :
          Array.isArray((raw as any)?.data) ? (raw as any).data :
            [];

    return list.map(mapPersonaToStrategy);
  },

  createPersona: async (payload: any) => {
    return apiFetch("/strategies/marketplace/create", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  togglePersona: async (personaId: string): Promise<{ status?: string; enabled?: boolean }> => {
    return apiFetch(`/strategies/marketplace/${personaId}/toggle`, {
      method: "PATCH",
    });
  },

  deletePersona: async (personaId: string) => {
    return apiFetch(`/strategies/marketplace/${personaId}`, {
      method: "DELETE",
    });
  },

  updatePersona: async (personaId: string, payload: { timeframe?: string; risk_profile?: string }) => {
    return apiFetch(`/strategies/marketplace/${personaId}/update`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  getHistory: async (personaId: string) => {
    return apiFetch(`/strategies/marketplace/${personaId}/history`);
  },
};