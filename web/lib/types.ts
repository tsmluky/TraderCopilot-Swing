export type Plan = 'FREE' | 'TRADER' | 'PRO'

export type Token = 'BTC' | 'ETH' | 'SOL' | 'BNB' | 'XRP'

export type Timeframe = '1H' | '4H' | '1D'

export type SignalType = 'LONG' | 'SHORT' | 'NEUTRAL'

export type EvaluationStatus = 'evaluated' | 'pending' | 'failed'

export interface Signal {
  id: string
  token: Token
  timeframe: Timeframe
  type: SignalType
  entryPrice: number
  entryRangeHigh?: number
  entryRangeLow?: number
  targetPrice: number
  stopLoss: number
  invalidation?: number
  confidence: number
  timestamp: Date
  status: 'ACTIVE' | 'CLOSED' | 'CANCELLED' | 'WATCH' | 'CREATED' | 'ARCHIVED'
  evaluation: EvaluationStatus
  pnl?: number
  rationale?: string
  indicators?: any
  watchlist?: WatchItem[]
}

export interface WatchItem {
  strategy_id: string
  token: string
  timeframe: string
  side: 'long' | 'short'
  distance_atr: number
  trigger_price: number
  close: number
  reason: string
  missing?: string[]
}

export interface Strategy {
  id: string
  name: string
  description: string
  winRate: number
  avgReturn: number
  signals: number
  expectedRoi?: string
  riskLevel?: string
  symbol?: string
  timeframes: Timeframe[]
  tokens: Token[]
  isActive: boolean
}

export interface User {
  id: string
  email: string
  name: string
  plan: Plan
  trialExpiresAt?: Date
  telegramConnected: boolean
  telegram_chat_id?: string
  telegram_username?: string
}

export interface PlanFeatures {
  tokens: Token[]
  timeframes: Timeframe[]
  hasAdvisor: boolean
  hasTelegram: boolean
  signalHistoryDays: number
}

export const PLAN_FEATURES: Record<Plan, PlanFeatures> = {
  FREE: {
    tokens: ['BTC', 'ETH'],
    timeframes: ['4H', '1D'],
    hasAdvisor: false,
    hasTelegram: false,
    signalHistoryDays: 7,
  },
  TRADER: {
    tokens: ['BTC', 'ETH', 'SOL', 'BNB', 'XRP'],
    timeframes: ['4H', '1D'],
    hasAdvisor: false,
    hasTelegram: true,
    signalHistoryDays: 30,
  },
  PRO: {
    tokens: ['BTC', 'ETH', 'SOL', 'BNB', 'XRP'],
    timeframes: ['1H', '4H', '1D'],
    hasAdvisor: true,
    hasTelegram: true,
    signalHistoryDays: 90,
  },
}

export const TOKEN_INFO: Record<Token, { name: string; color: string }> = {
  BTC: { name: 'Bitcoin', color: '#F7931A' },
  ETH: { name: 'Ethereum', color: '#627EEA' },
  SOL: { name: 'Solana', color: '#9945FF' },
  BNB: { name: 'BNB', color: '#F3BA2F' },
  XRP: { name: 'XRP', color: '#23292F' },
}
