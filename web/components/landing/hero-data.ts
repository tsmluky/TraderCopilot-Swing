import { LucideIcon } from 'lucide-react'

// Dummy data for the floating cards to avoid complex imports in the visual component
export const MOCK_SIGNAL = {
    pair: 'BTC/USDT',
    type: 'LONG',
    entry: 97250,
    target: 105000,
    stop: 94200,
    confidence: 92,
    roi: 450
}

export const MOCK_PERFORMANCE = [
    { date: 'Jan', value: 100 },
    { date: 'Feb', value: 120 },
    { date: 'Mar', value: 115 },
    { date: 'Apr', value: 140 },
    { date: 'May', value: 165 },
    { date: 'Jun', value: 190 },
]

export const MOCK_SCANNED_ITEMS = [
    { symbol: 'SOL', status: 'Verifying', score: 85 },
    { symbol: 'AVAX', status: 'Scanning', score: 45 },
    { symbol: 'LINK', status: 'Found Setup', score: 91 },
]
