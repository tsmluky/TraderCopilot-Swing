'use client'

import { ArrowUpRight, ArrowDownRight, Lock, Clock, Check, Loader2, X, AlertTriangle, TrendingUp } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { useUser } from '@/lib/user-context'
import type { Signal, EvaluationStatus } from '@/lib/types'
import { formatPrice, timeAgo, TOKEN_INFO } from '@/lib/mock-data'

interface SignalCardProps {
  signal: Signal
  compact?: boolean
}

function EvaluationBadge({ status }: { status: EvaluationStatus }) {
  const config = {
    evaluated: {
      label: 'Evaluated',
      icon: Check,
      className: 'badge-success',
    },
    pending: {
      label: 'Pending',
      icon: Loader2,
      className: 'bg-warning-muted text-warning border-warning/20',
      animate: true,
    },
    failed: {
      label: 'Failed',
      icon: X,
      className: 'bg-short-muted text-short border-short/20',
    },
  }

  const { label, icon: Icon, className, animate } = config[status] as {
    label: string
    icon: typeof Check
    className: string
    animate?: boolean
  }

  return (
    <span className={cn(
      'inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[10px] font-medium',
      className
    )}>
      <Icon className={cn('h-2.5 w-2.5', animate && 'animate-spin')} />
      {label}
    </span>
  )
}

export function SignalCard({ signal, compact = false }: SignalCardProps) {
  const { canAccessToken, canAccessTimeframe } = useUser()

  const isTokenLocked = !canAccessToken(signal.token)
  const isTimeframeLocked = !canAccessTimeframe(signal.timeframe)
  const isLocked = isTokenLocked || isTimeframeLocked

  const tokenInfo = TOKEN_INFO[signal.token] || { name: signal.token, color: '#888' }
  const isLong = signal.type === 'LONG'
  const isShort = signal.type === 'SHORT'
  const isNeutral = signal.type === 'NEUTRAL'

  // Clean raw audit markers from rationale for display
  const displayRationale = signal.rationale?.replace(/\| AUDIT:.*$/, '')?.trim() || "No rationale provided."

  // Locked state
  if (isLocked) {
    return (
      <div className="group relative overflow-hidden rounded-xl border border-dashed border-border/50 bg-muted/30 p-6">
        <div className="flex flex-col items-center justify-center text-center min-h-[160px]">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted mb-3">
            <Lock className="h-5 w-5 text-muted-foreground" />
          </div>
          <p className="text-sm font-medium text-muted-foreground mb-1">
            {isTokenLocked ? `${signal.token} Signals` : '1H Timeframe'}
          </p>
          <p className="text-xs text-muted-foreground/60">
            {isTokenLocked ? 'Upgrade to SwingLite' : 'Upgrade to SwingPro'}
          </p>
        </div>
      </div>
    )
  }

  // NEUTRAL State (Simplified Card)
  if (isNeutral) {
    return (
      <div className="group relative overflow-hidden rounded-xl border border-border/50 bg-card/50 transition-all duration-300 hover:border-border hover:bg-card">
        <div className="p-4 flex flex-col gap-3 min-h-[140px]">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-2">
              <div
                className="flex h-8 w-8 items-center justify-center rounded-lg text-[10px] font-bold shrink-0"
                style={{ backgroundColor: `${tokenInfo.color}10`, color: tokenInfo.color }}
              >
                {signal.token}
              </div>
              <span className="font-semibold text-sm">{signal.token}</span>
              <span className="rounded bg-secondary px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                {signal.timeframe}
              </span>
            </div>
            <Badge variant="outline" className="text-xs text-muted-foreground border-border">
              Neutral
            </Badge>
          </div>

          <div className="flex-1 flex items-center justify-center text-center p-2 rounded-lg bg-secondary/20 border border-dashed border-border/50">
            <p className="text-xs text-muted-foreground leading-relaxed line-clamp-3">
              {displayRationale}
            </p>
          </div>
          <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
            <Clock className="h-3 w-3" />
            <span>{timeAgo(signal.timestamp)}</span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={cn(
      'group relative overflow-hidden rounded-xl border border-border/50 bg-card transition-all duration-300',
      'hover:border-border hover:shadow-soft-md'
    )}>
      {/* Top accent line based on signal type */}
      <div className={cn(
        'absolute top-0 left-0 right-0 h-px',
        isLong ? 'bg-gradient-to-r from-transparent via-long to-transparent' : 'bg-gradient-to-r from-transparent via-short to-transparent'
      )} />

      {/* Header */}
      <div className="p-4 pb-3">
        <div className="flex items-start justify-between gap-3">
          {/* Token info */}
          <div className="flex items-center gap-3">
            <div
              className="flex h-10 w-10 items-center justify-center rounded-lg text-xs font-bold shrink-0"
              style={{ backgroundColor: `${tokenInfo.color}12`, color: tokenInfo.color }}
            >
              {signal.token}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-foreground">{signal.token}/USDT</span>
                <span className="rounded bg-secondary px-1.5 py-0.5 text-[10px] font-medium text-secondary-foreground">
                  {signal.timeframe}
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">{tokenInfo.name}</p>
            </div>
          </div>

          {/* Direction badge */}
          <div className="flex flex-col items-end gap-1.5 shrink-0">
            <span
              className={cn(
                'inline-flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-semibold whitespace-nowrap',
                isLong
                  ? 'badge-long'
                  : 'badge-short'
              )}
            >
              {isLong ? (
                <ArrowUpRight className="h-3.5 w-3.5" />
              ) : (
                <ArrowDownRight className="h-3.5 w-3.5" />
              )}
              {signal.type}
            </span>
            <div className="max-w-[100px] flex justify-end">
              <EvaluationBadge status={signal.evaluation} />
            </div>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="px-4 pb-4 space-y-3">
        {/* Entry range - highlighted */}
        <div className="rounded-lg bg-secondary/50 p-3">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
              Entry Range
            </span>
            <TrendingUp className="h-3.5 w-3.5 text-muted-foreground/50" />
          </div>
          <div className="flex items-baseline gap-2 flex-wrap">
            <span className="text-lg font-mono font-semibold text-foreground tabular-nums">
              ${formatPrice(signal.entryPrice)}
            </span>
            {signal.entryRangeLow && signal.entryRangeHigh && (
              <span className="text-xs text-muted-foreground font-mono tabular-nums whitespace-nowrap">
                ${formatPrice(signal.entryRangeLow)} - ${formatPrice(signal.entryRangeHigh)}
              </span>
            )}
          </div>
        </div>

        {/* Targets grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
              Target
            </span>
            <p className="text-sm font-mono font-semibold text-success tabular-nums truncate">
              ${formatPrice(signal.targetPrice)}
            </p>
          </div>
          <div className="space-y-1">
            <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
              Stop Loss
            </span>
            <p className="text-sm font-mono font-semibold text-destructive tabular-nums truncate">
              ${formatPrice(signal.stopLoss)}
            </p>
          </div>
        </div>

        {/* Invalidation */}
        {signal.invalidation && (
          <div className="flex items-center gap-1.5 rounded-md bg-warning-muted/50 px-2.5 py-1.5">
            <AlertTriangle className="h-3 w-3 text-warning shrink-0" />
            <span className="text-[11px] text-warning truncate">
              Invalidation: <span className="font-mono font-medium">${formatPrice(signal.invalidation)}</span>
            </span>
          </div>
        )}

        {/* Rationale (if present and not covered elsewhere) */}
        {/* Optional: Add small Rationale snippet here if desired? Users like context. */}
        {/* For now, just Confidence. */}

        {/* Confidence meter */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">
              Confidence
            </span>
            <span className="text-xs font-semibold text-foreground tabular-nums">
              {signal.confidence}%
            </span>
          </div>
          <div className="h-1.5 w-full rounded-full bg-secondary">
            <div
              className={cn(
                'h-full rounded-full transition-all duration-500',
                signal.confidence >= 80 ? 'bg-success' : signal.confidence >= 60 ? 'bg-primary' : 'bg-warning'
              )}
              style={{ width: `${signal.confidence}%` }}
            />
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between border-t border-border/50 px-4 py-3">
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Clock className="h-3 w-3" />
          <span>{timeAgo(signal.timestamp)}</span>
        </div>
        {signal.status === 'ACTIVE' && (
          <span className="flex items-center gap-1.5 text-xs font-medium text-success">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-success" />
            </span>
            Active
          </span>
        )}
      </div>
    </div>
  )
}
