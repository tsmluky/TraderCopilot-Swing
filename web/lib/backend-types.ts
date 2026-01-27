// Backend DTOs (safe subset) aligned to TraderCopilot-Swing OpenAPI.
// Keep this file narrow: it exists to decouple the UI from backend/internal ORM shapes.

export type BackendUser = {
  id: number;
  email: string;
  name: string;
  role: string;
  plan: string; // FREE | TRADER | PRO (or others)
  allowed_tokens?: string[] | null;
  telegram_chat_id?: string | null;
  telegram_username?: string | null;
  timezone?: string | null;
  plan_expires_at?: string | null;
  created_at: string;
};

export type Entitlements = {
  tier: string; // tier_trial | tier_trader | tier_pro | tier_trial_expired
  plan_label: string; // canonical label used by backend (often same as plan)
  expires_at?: string | null;
  features?: Record<
    string,
    {
      limit: number;
      used: number;
      remaining: number;
    }
  >;
  allowed_tokens: string[];
  allowed_timeframes: string[];
  is_trial_expired: boolean;
  telegram_access: boolean;
  advisor_access: boolean;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  // Some builds return user inline. Others don't. We tolerate both.
  user?: BackendUser;
};
