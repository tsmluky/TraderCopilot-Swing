'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { RefreshCw, Sparkles, TrendingUp } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { SignalCard } from './signal-card'
import { Signal } from '@/lib/types'
import type { Token, Timeframe } from '@/lib/types'

interface SignalsFeedProps {
  selectedToken: Token | 'ALL'
  selectedTimeframe: Timeframe | 'ALL'
  signals: Signal[]
  isLoading?: boolean
  onRefresh: () => void
}

export function SignalsFeed({
  selectedToken,
  selectedTimeframe,
  signals,
  isLoading,
  onRefresh,
}: SignalsFeedProps) {
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Filter signals based on selections
  const filteredSignals = signals.filter((signal) => {
    const tokenMatch = selectedToken === 'ALL' || signal.token === selectedToken
    const timeframeMatch = selectedTimeframe === 'ALL' || signal.timeframe === selectedTimeframe
    return tokenMatch && timeframeMatch
  })

  const handleRefresh = () => {
    // UX: mostrar estado de refresco aunque el refresh sea instantáneo
    setIsRefreshing(true)
    try {
      onRefresh()
    } finally {
      setTimeout(() => setIsRefreshing(false), 800)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between">
          <div className="h-6 w-32 bg-muted rounded animate-pulse" />
          <div className="h-8 w-24 bg-muted rounded animate-pulse" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-[280px] rounded-xl border border-border/50 bg-card/50 animate-pulse"
            />
          ))}
        </div>
      </div>
    )
  }

  // Empty state
  if (filteredSignals.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted/50 border border-border">
          <TrendingUp className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold text-foreground mb-1">No signals yet</h3>
        <p className="text-sm text-muted-foreground mb-6 max-w-xs">
          No signals match your current filters. Try adjusting your token or timeframe selection.
        </p>
        <Link href="/dashboard/signals">
          <Button className="gap-2">
            <Sparkles className="h-4 w-4" />
            Generate first signal
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-foreground">Latest Signals</h2>
          <p className="text-sm text-muted-foreground">
            {filteredSignals.length} active signal{filteredSignals.length !== 1 ? 's' : ''}
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="gap-2 bg-transparent"
        >
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          {isRefreshing ? 'Refreshing' : 'Refresh'}
        </Button>
      </div>

      {/* Signal Grid */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {filteredSignals.map((signal) => (
          <SignalCard key={signal.id} signal={signal} />
        ))}
      </div>
    </div>
  )
}
