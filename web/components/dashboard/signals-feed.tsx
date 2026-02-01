'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { RefreshCw, Sparkles, TrendingUp, ChevronLeft, ChevronRight } from 'lucide-react'
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

const ITEMS_PER_PAGE = 12

export function SignalsFeed({
  selectedToken,
  selectedTimeframe,
  signals,
  isLoading,
  onRefresh,
}: SignalsFeedProps) {
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)

  // Filter signals based on selections
  const filteredSignals = signals.filter((signal) => {
    const tokenMatch = selectedToken === 'ALL' || signal.token === selectedToken
    const timeframeMatch = selectedTimeframe === 'ALL' || signal.timeframe === selectedTimeframe
    return tokenMatch && timeframeMatch
  })

  // Calculate stats
  const activeCount = filteredSignals.filter(s =>
    s.status === 'ACTIVE' || s.status === 'WATCH' || s.status === 'CREATED'
  ).length

  // Pagination Logic
  const totalPages = Math.ceil(filteredSignals.length / ITEMS_PER_PAGE)
  const paginatedSignals = filteredSignals.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  )

  // Reset page when filters change
  React.useEffect(() => {
    setCurrentPage(1)
  }, [selectedToken, selectedTimeframe])

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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-foreground">Latest Signals</h2>
          <p className="text-sm text-muted-foreground">
            {activeCount} active signal{activeCount !== 1 ? 's' : ''} <span className="opacity-50">• {filteredSignals.length} total</span>
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
      <div className="grid gap-3 grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
        {paginatedSignals.map((signal) => (
          <SignalCard key={signal.id} signal={signal} />
        ))}
      </div>

      {/* Pagination Footer */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-border/40 pt-4">
          <p className="text-xs text-muted-foreground">
            Showing {((currentPage - 1) * ITEMS_PER_PAGE) + 1} to {Math.min(currentPage * ITEMS_PER_PAGE, filteredSignals.length)} of {filteredSignals.length} signals
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-xs font-medium min-w-[3rem] text-center">
              Page {currentPage} / {totalPages}
            </span>
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8"
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
