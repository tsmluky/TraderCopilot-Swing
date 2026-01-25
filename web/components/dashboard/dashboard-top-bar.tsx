'use client'

import Link from 'next/link'
import { Lock, ArrowUpRight, Filter } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { PlanBadge } from '@/components/plan-badge'
import { useUser } from '@/lib/user-context'
import { PLAN_FEATURES, TOKEN_INFO } from '@/lib/types'
import type { Token, Timeframe } from '@/lib/types'
import { cn } from '@/lib/utils'

const ALL_TOKENS: Token[] = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP']
const ALL_TIMEFRAMES: Timeframe[] = ['1H', '4H', '1D']

interface DashboardTopBarProps {
  selectedToken: Token | 'ALL'
  selectedTimeframe: Timeframe | 'ALL'
  onTokenChange: (token: Token | 'ALL') => void
  onTimeframeChange: (timeframe: Timeframe | 'ALL') => void
}

export function DashboardTopBar({
  selectedToken,
  selectedTimeframe,
  onTokenChange,
  onTimeframeChange,
}: DashboardTopBarProps) {
  const { user } = useUser()
  // Adjust features to safe defaults
  const features = (user ? PLAN_FEATURES[user.plan] : PLAN_FEATURES.FREE) || { tokens: [], timeframes: [] }

  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-black/5 dark:border-white/5">
      {/* Token and Timeframe Selectors */}
      <div className="flex flex-wrap items-center gap-4">

        {/* Token Selector */}
        <div className="bg-black/5 dark:bg-black/20 backdrop-blur-md p-1 rounded-xl border border-black/5 dark:border-white/5 flex items-center">
          <span className="px-3 text-[10px] font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5 opacity-50">
            Token
          </span>
          <button
            onClick={() => onTokenChange('ALL')}
            className={cn(
              'px-3 py-1.5 text-xs font-bold rounded-lg transition-all duration-300',
              selectedToken === 'ALL'
                ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20'
                : 'text-muted-foreground hover:text-foreground hover:bg-black/5 dark:hover:bg-white/5'
            )}
          >
            All
          </button>
          <div className="w-px h-4 bg-black/10 dark:bg-white/10 mx-1" />
          {ALL_TOKENS.map((token) => {
            const isAvailable = features.tokens.includes(token)
            return (
              <button
                key={token}
                onClick={() => isAvailable && onTokenChange(token)}
                disabled={!isAvailable}
                className={cn(
                  'px-3 py-1.5 text-xs font-bold rounded-lg transition-all flex items-center gap-1.5',
                  selectedToken === token
                    ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20'
                    : isAvailable
                      ? 'text-muted-foreground hover:text-foreground hover:bg-black/5 dark:hover:bg-white/5'
                      : 'text-muted-foreground/30 cursor-not-allowed'
                )}
                title={!isAvailable ? 'Upgrade to access' : token}
              >
                {token}
                {!isAvailable && <Lock className="h-2.5 w-2.5 opacity-70" />}
              </button>
            )
          })}
        </div>

        {/* Timeframe Selector */}
        <div className="bg-black/5 dark:bg-black/20 backdrop-blur-md p-1 rounded-xl border border-black/5 dark:border-white/5 flex items-center">
          <span className="px-3 text-[10px] font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5 opacity-50">
            TF
          </span>
          <button
            onClick={() => onTimeframeChange('ALL')}
            className={cn(
              'px-3 py-1.5 text-xs font-bold rounded-lg transition-all duration-300',
              selectedTimeframe === 'ALL'
                ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20'
                : 'text-muted-foreground hover:text-foreground hover:bg-black/5 dark:hover:bg-white/5'
            )}
          >
            All
          </button>
          <div className="w-px h-4 bg-black/10 dark:bg-white/10 mx-1" />
          {ALL_TIMEFRAMES.map((tf) => {
            const isAvailable = features.timeframes.includes(tf)
            return (
              <button
                key={tf}
                onClick={() => isAvailable && onTimeframeChange(tf)}
                disabled={!isAvailable}
                className={cn(
                  'px-3 py-1.5 text-xs font-bold rounded-lg transition-all flex items-center gap-1.5',
                  selectedTimeframe === tf
                    ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20'
                    : isAvailable
                      ? 'text-muted-foreground hover:text-foreground hover:bg-black/5 dark:hover:bg-white/5'
                      : 'text-muted-foreground/30 cursor-not-allowed'
                )}
                title={!isAvailable ? 'Upgrade required' : `${tf} timeframe`}
              >
                {tf}
                {!isAvailable && <Lock className="h-2.5 w-2.5 opacity-70" />}
              </button>
            )
          })}
        </div>
      </div>

      {/* Upgrade Button (Only for Non-PRO) */}
      <div className="flex items-center gap-3">
        {user?.plan !== 'PRO' && (
          <Link href="/pricing">
            <Button size="sm" className="gap-2 h-9 px-4 bg-gradient-to-r from-primary to-blue-600 border-0 shadow-lg shadow-primary/20 hover:scale-105 transition-all">
              Unlock Full Access
              <ArrowUpRight className="h-3.5 w-3.5 opacity-70" />
            </Button>
          </Link>
        )}
      </div>
    </div>
  )
}
