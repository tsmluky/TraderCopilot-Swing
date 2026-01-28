import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

// --- API CLIENT ---
// Normaliza NEXT_PUBLIC_API_BASE_URL para evitar URLs relativas si falta el esquema.
// - Si falta esquema y es localhost/127.0.0.1 -> http://
// - Si falta esquema y es dominio -> https://
// - Siempre elimina trailing slashes

function normalizeBaseUrl(raw: string | undefined | null): string {
    const v = String(raw ?? "").trim().replace(/\/+$/, "");
    if (!v) return "http://localhost:8000";

    if (v.startsWith("http://") || v.startsWith("https://")) {
        return v.replace(/\/+$/, "");
    }

    // Sin esquema -> decide según host
    const lower = v.toLowerCase();
    if (lower.startsWith("localhost") || lower.startsWith("127.0.0.1")) {
        return `http://${v}`.replace(/\/+$/, "");
    }

    return `https://${v}`.replace(/\/+$/, "");
}

export const BASE_URL = normalizeBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL);

export class AuthError extends Error {
    constructor(message = "Unauthorized") {
        super(message);
        this.name = "AuthError";
    }
}

export class AccessError extends Error {
    code?: string;
    constructor(message: string, code?: string) {
        super(message);
        this.name = "AccessError";
        this.code = code;
    }
}

export class ApiError extends Error {
    status: number;
    constructor(message: string, status: number) {
        super(message);
        this.name = "ApiError";
        this.status = status;
    }
}

interface FetchOptions extends RequestInit {
    params?: Record<string, string | number | boolean | undefined | null>;
    timeoutMs?: number;
}

/** Cookie getter (client-side only). */
function getCookie(name: string): string | null {
    if (typeof document === "undefined") return null;
    const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const match = document.cookie.match(new RegExp(`(?:^|; )${escaped}=([^;]*)`));
    return match ? decodeURIComponent(match[1]) : null;
}

/** Safely read JSON (or return null if not JSON / empty). */
async function readJsonSafe(res: Response): Promise<any | null> {
    const ct = res.headers.get("content-type") || "";
    if (!ct.includes("application/json")) {
        return null;
    }
    try {
        return await res.json();
    } catch {
        return null;
    }
}

function normalizeFastApiError(data: any | null): { message: string; code?: string } {
    if (!data) return { message: "Unexpected error" };

    const d = data.detail;

    // FastAPI: detail can be string | object | array
    if (typeof d === "string") return { message: d };

    if (Array.isArray(d)) {
        const msgs = d
            .map((x) => (x && typeof x === "object" ? x.msg : String(x)))
            .filter(Boolean);
        return { message: msgs.join(" | ") || "Validation error" };
    }

    if (d && typeof d === "object") {
        return {
            message: d.message || d.error || JSON.stringify(d),
            code: d.code,
        };
    }

    // fallback: maybe backend returns {message, code}
    if (typeof data.message === "string") {
        return { message: data.message, code: data.code };
    }

    return { message: "Unexpected error" };
}

export async function apiFetch<T = any>(
    endpoint: string,
    { params, headers, timeoutMs = 60000, ...customConfig }: FetchOptions = {}
): Promise<T> {
    const token =
        typeof window !== "undefined"
            ? (localStorage.getItem("tc_token") || getCookie("tc_token"))
            : null;

    const headersConfig: HeadersInit = {
        ...(customConfig.body ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...headers,
    };

    // Remove Content-Type if body is FormData or URLSearchParams
    if (customConfig.body instanceof URLSearchParams || customConfig.body instanceof FormData) {
        if (headersConfig instanceof Headers) headersConfig.delete("Content-Type");
        else if (!Array.isArray(headersConfig)) {
            delete (headersConfig as Record<string, string>)["Content-Type"];
        }
    }

    let url = `${BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

    if (params) {
        const searchParams = new URLSearchParams();
        for (const [k, v] of Object.entries(params)) {
            if (v === undefined || v === null) continue;
            searchParams.append(k, String(v));
        }
        const qs = searchParams.toString();
        if (qs) url += `?${qs}`;
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);

    try {
        const res = await fetch(url, {
            method: "GET",
            headers: headersConfig,
            signal: controller.signal,
            ...customConfig,
        });

        // 401 -> throw only; AuthContext decides redirect/logout
        if (res.status === 401) {
            throw new AuthError("Session expired or invalid credentials.");
        }

        const data = await readJsonSafe(res);

        if (!res.ok) {
            const norm = normalizeFastApiError(data);

            if (res.status === 403) {
                throw new AccessError(norm.message, norm.code);
            }
            throw new ApiError(norm.message, res.status);
        }

        return (data ?? ({} as any)) as T;
    } catch (err: any) {
        if (err?.name === "AbortError") {
            throw new Error("Request timeout");
        }
        if (err instanceof AuthError || err instanceof AccessError || err instanceof ApiError) {
            throw err;
        }
        throw new Error(err instanceof Error ? err.message : "Network error");
    } finally {
        clearTimeout(timeout);
    }
}
