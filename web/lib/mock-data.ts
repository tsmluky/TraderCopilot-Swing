import type { Signal, Strategy, Token, Timeframe, EvaluationStatus } from './types'

export { TOKEN_INFO } from './types'

export const mockSignals: Signal[] = [
  {
    id: '1',
    token: 'BTC',
    timeframe: '4H',
    type: 'LONG',
    entryPrice: 67450,
    entryRangeHigh: 67600,
    entryRangeLow: 67300,
    targetPrice: 71200,
    stopLoss: 65800,
    invalidation: 65500,
    confidence: 78,
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    status: 'ACTIVE',
    evaluation: 'evaluated',
  },
  {
    id: '2',
    token: 'ETH',
    timeframe: '1D',
    type: 'LONG',
    entryPrice: 3520,
    entryRangeHigh: 3550,
    entryRangeLow: 3490,
    targetPrice: 3850,
    stopLoss: 3380,
    invalidation: 3350,
    confidence: 82,
    timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
    status: 'ACTIVE',
    evaluation: 'evaluated',
  },
  {
    id: '3',
    token: 'SOL',
    timeframe: '4H',
    type: 'SHORT',
    entryPrice: 148.5,
    entryRangeHigh: 150.0,
    entryRangeLow: 147.0,
    targetPrice: 138.0,
    stopLoss: 154.0,
    invalidation: 156.0,
    confidence: 71,
    timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000),
    status: 'ACTIVE',
    evaluation: 'pending',
  },
  {
    id: '4',
    token: 'BNB',
    timeframe: '1D',
    type: 'LONG',
    entryPrice: 612,
    entryRangeHigh: 620,
    entryRangeLow: 605,
    targetPrice: 680,
    stopLoss: 580,
    invalidation: 570,
    confidence: 75,
    timestamp: new Date(Date.now() - 18 * 60 * 60 * 1000),
    status: 'ACTIVE',
    evaluation: 'evaluated',
  },
  {
    id: '5',
    token: 'XRP',
    timeframe: '4H',
    type: 'LONG',
    entryPrice: 0.52,
    entryRangeHigh: 0.525,
    entryRangeLow: 0.515,
    targetPrice: 0.58,
    stopLoss: 0.49,
    invalidation: 0.485,
    confidence: 68,
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
    status: 'ACTIVE',
    evaluation: 'failed',
  },
  {
    id: '6',
    token: 'BTC',
    timeframe: '1H',
    type: 'SHORT',
    entryPrice: 68200,
    entryRangeHigh: 68400,
    entryRangeLow: 68000,
    targetPrice: 66500,
    stopLoss: 69100,
    invalidation: 69500,
    confidence: 65,
    timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000),
    status: 'ACTIVE',
    evaluation: 'pending',
  },
]

export const mockClosedSignals: Signal[] = [
  {
    id: '101',
    token: 'BTC',
    timeframe: '4H',
    type: 'LONG',
    entryPrice: 64200,
    entryRangeHigh: 64400,
    entryRangeLow: 64000,
    targetPrice: 67500,
    stopLoss: 62800,
    invalidation: 62500,
    confidence: 76,
    timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    status: 'CLOSED',
    evaluation: 'evaluated',
    pnl: 5.14,
  },
  {
    id: '102',
    token: 'ETH',
    timeframe: '1D',
    type: 'LONG',
    entryPrice: 3280,
    entryRangeHigh: 3300,
    entryRangeLow: 3260,
    targetPrice: 3550,
    stopLoss: 3150,
    invalidation: 3120,
    confidence: 79,
    timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    status: 'CLOSED',
    evaluation: 'evaluated',
    pnl: 8.23,
  },
  {
    id: '103',
    token: 'SOL',
    timeframe: '4H',
    type: 'SHORT',
    entryPrice: 162,
    entryRangeHigh: 164,
    entryRangeLow: 160,
    targetPrice: 148,
    stopLoss: 170,
    invalidation: 172,
    confidence: 72,
    timestamp: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
    status: 'CLOSED',
    evaluation: 'failed',
    pnl: -4.94,
  },
  {
    id: '104',
    token: 'BTC',
    timeframe: '1D',
    type: 'LONG',
    entryPrice: 61500,
    entryRangeHigh: 61800,
    entryRangeLow: 61200,
    targetPrice: 65000,
    stopLoss: 59500,
    invalidation: 59000,
    confidence: 81,
    timestamp: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000),
    status: 'CLOSED',
    evaluation: 'evaluated',
    pnl: 5.69,
  },
]

export const mockStrategies: Strategy[] = [
  {
    id: '1',
    name: 'Momentum Breakout',
    description: 'Identifies strong momentum shifts using volume and price action on higher timeframes for swing entries.',
    winRate: 68,
    avgReturn: 4.2,
    signals: 156,
    timeframes: ['4H', '1D'],
    tokens: ['BTC', 'ETH', 'SOL', 'BNB', 'XRP'],
  },
  {
    id: '2',
    name: 'Support/Resistance Reversal',
    description: 'Detects key support and resistance levels with confluence from multiple indicators for high-probability reversals.',
    winRate: 72,
    avgReturn: 3.8,
    signals: 203,
    timeframes: ['4H', '1D'],
    tokens: ['BTC', 'ETH', 'SOL', 'BNB', 'XRP'],
  },
  {
    id: '3',
    name: 'Trend Continuation',
    description: 'Follows established trends with pullback entries, optimized for swing positions in trending markets.',
    winRate: 65,
    avgReturn: 5.1,
    signals: 124,
    timeframes: ['1H', '4H', '1D'],
    tokens: ['BTC', 'ETH', 'SOL', 'BNB', 'XRP'],
  },
  {
    id: '4',
    name: 'Multi-Timeframe Confluence',
    description: 'Combines signals from multiple timeframes to identify high-confidence swing opportunities.',
    winRate: 74,
    avgReturn: 4.6,
    signals: 89,
    timeframes: ['1H', '4H', '1D'],
    tokens: ['BTC', 'ETH'],
  },
]

export const kpiData = {
  totalSignals: 487,
  winRate: 69.4,
  avgReturn: 4.3,
  activeSignals: 6,
  profitFactor: 2.14,
  maxDrawdown: -12.3,
  last7dSignals: 12,
}

export const tokenPrices: Record<Token, { price: number; change24h: number }> = {
  BTC: { price: 67892.45, change24h: 2.34 },
  ETH: { price: 3542.18, change24h: 1.87 },
  SOL: { price: 147.82, change24h: -0.92 },
  BNB: { price: 618.45, change24h: 1.23 },
  XRP: { price: 0.5234, change24h: 3.45 },
}

export function formatPrice(price: number): string {
  if (price < 1) return price.toFixed(4)
  if (price < 100) return price.toFixed(2)
  return price.toLocaleString('en-US', { maximumFractionDigits: 2 })
}

export function formatPercent(value: number): string {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

export function timeAgo(date: Date): string {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000)
  
  if (seconds < 60) return 'Just now'
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  return `${Math.floor(seconds / 86400)}d ago`
}
