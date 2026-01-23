'use client'

import Link from 'next/link'
import { Lock, ArrowUpRight } from 'lucide-react'
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
  const features = (user ? PLAN_FEATURES[user.plan] : PLAN_FEATURES.FREE) || { tokens: [], timeframes: [] }

  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-border">
      {/* Token and Timeframe Selectors */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Token Selector */}
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide mr-1">Token</span>
          <div className="flex items-center gap-1 rounded-lg bg-secondary/50 p-1">
            <button
              onClick={() => onTokenChange('ALL')}
              className={cn(
                'px-2.5 py-1 text-xs font-medium rounded-md transition-all',
                selectedToken === 'ALL'
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent'
              )}
            >
              All
            </button>
            {ALL_TOKENS.map((token) => {
              const isAvailable = features.tokens.includes(token)
              const tokenInfo = TOKEN_INFO[token]
              return (
                <button
                  key={token}
                  onClick={() => isAvailable && onTokenChange(token)}
                  disabled={!isAvailable}
                  className={cn(
                    'px-2.5 py-1 text-xs font-medium rounded-md transition-all flex items-center gap-1',
                    selectedToken === token
                      ? 'bg-primary text-primary-foreground'
                      : isAvailable
                        ? 'text-muted-foreground hover:text-foreground hover:bg-accent'
                        : 'text-muted-foreground/40 cursor-not-allowed'
                  )}
                  title={!isAvailable ? 'Upgrade to access' : tokenInfo.name}
                >
                  {token}
                  {!isAvailable && <Lock className="h-2.5 w-2.5" />}
                </button>
              )
            })}
          </div>
        </div>

        {/* Timeframe Selector */}
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide mr-1">TF</span>
          <div className="flex items-center gap-1 rounded-lg bg-secondary/50 p-1">
            <button
              onClick={() => onTimeframeChange('ALL')}
              className={cn(
                'px-2.5 py-1 text-xs font-medium rounded-md transition-all',
                selectedTimeframe === 'ALL'
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent'
              )}
            >
              All
            </button>
            {ALL_TIMEFRAMES.map((tf) => {
              const isAvailable = features.timeframes.includes(tf)
              const isPro = tf === '1H'
              return (
                <button
                  key={tf}
                  onClick={() => isAvailable && onTimeframeChange(tf)}
                  disabled={!isAvailable}
                  className={cn(
                    'px-2.5 py-1 text-xs font-medium rounded-md transition-all flex items-center gap-1',
                    selectedTimeframe === tf
                      ? 'bg-primary text-primary-foreground'
                      : isAvailable
                        ? 'text-muted-foreground hover:text-foreground hover:bg-accent'
                        : 'text-muted-foreground/40 cursor-not-allowed'
                  )}
                  title={!isAvailable ? '1H requires SwingPro' : `${tf} timeframe`}
                >
                  {tf}
                  {!isAvailable && isPro && <Lock className="h-2.5 w-2.5" />}
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* Upgrade Button (Only for Non-PRO) */}
      <div className="flex items-center gap-3">
        {user?.plan !== 'PRO' && (
          <Link href="/pricing">
            <Button size="sm" className="gap-1.5 h-8">
              Upgrade
              <ArrowUpRight className="h-3.5 w-3.5" />
            </Button>
          </Link>
        )}
      </div>
    </div>
  )
}
