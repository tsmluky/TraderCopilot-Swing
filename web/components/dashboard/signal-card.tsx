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
      'inline-flex items-center gap-1 rounded-md border px-1 py-0.5 text-[9px] font-bold uppercase tracking-wider',
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

  // Normalize confidence (handle 0-1 vs 0-100)
  const confidenceValue = signal.confidence <= 1 ? signal.confidence * 100 : signal.confidence
  const displayConfidence = Math.round(confidenceValue)

  // Clean raw audit markers from rationale for display
  const displayRationale = signal.rationale?.replace(/\| AUDIT:.*$/, '')?.trim() || "No rationale provided."

  // Locked state
  if (isLocked) {
    return (
      <div className="group relative overflow-hidden rounded-xl border border-dashed border-black/10 dark:border-border/50 bg-secondary/10 dark:bg-muted/30 p-4">
        <div className="flex flex-col items-center justify-center text-center min-h-[140px]">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary mb-2">
            <Lock className="h-4 w-4 text-muted-foreground" />
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
      <div className="group relative overflow-hidden rounded-xl border border-black/5 dark:border-border/50 bg-white dark:bg-card/50 transition-all duration-300 hover:border-border hover:bg-card shadow-sm dark:shadow-none">
        <div className="p-3 flex flex-col gap-3 min-h-[130px]">
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

  // Default Active Layout (Compacted)
  return (
    <div className={cn(
      'group relative overflow-hidden rounded-xl border border-black/5 dark:border-border/50 bg-white dark:bg-card transition-all duration-300',
      'hover:border-black/10 dark:hover:border-border hover:shadow-md dark:hover:shadow-soft-md shadow-sm dark:shadow-none'
    )}>
      {/* Top accent line based on signal type */}
      <div className={cn(
        'absolute top-0 left-0 right-0 h-px',
        isLong ? 'bg-gradient-to-r from-transparent via-emerald-500 to-transparent' : 'bg-gradient-to-r from-transparent via-rose-500 to-transparent'
      )} />

      {/* Header */}
      <div className="p-3 pb-2">
        <div className="flex items-start justify-between gap-1">
          {/* Token info */}
          <div className="flex items-center gap-2 overflow-hidden">
            <div
              className="flex h-8 w-8 items-center justify-center rounded-lg text-xs font-bold shrink-0"
              style={{ backgroundColor: `${tokenInfo.color}12`, color: tokenInfo.color }}
            >
              {signal.token}
            </div>
            <div className="min-w-0 flex flex-col justify-center">
              <span className="font-medium text-sm text-foreground leading-none">{tokenInfo.name}</span>
              <span className="text-[10px] text-muted-foreground mt-0.5">
                USDT • {signal.timeframe}
              </span>
            </div>
          </div>

          {/* Direction badge */}
          <div className="flex flex-col items-end gap-1 shrink-0 ml-1">
            <span
              className={cn(
                'inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider whitespace-nowrap',
                isLong
                  ? 'badge-long'
                  : 'badge-short'
              )}
            >
              {isLong ? (
                <ArrowUpRight className="h-3 w-3" />
              ) : (
                <ArrowDownRight className="h-3 w-3" />
              )}
              {signal.type}
            </span>
            <div className="flex justify-end">
              <EvaluationBadge status={signal.evaluation} />
            </div>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="px-3 pb-3 space-y-2">
        {/* Entry range - highlighted */}
        <div className="rounded-lg bg-secondary/50 p-2">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">
              Entry
            </span>
            <TrendingUp className="h-3 w-3 text-muted-foreground/50" />
          </div>
          <div className="flex items-baseline gap-2 flex-wrap">
            <span className="text-base font-mono font-bold text-foreground tabular-nums">
              ${formatPrice(signal.entryPrice)}
            </span>
            {signal.entryRangeLow && signal.entryRangeHigh && (
              <span className="text-[10px] text-muted-foreground font-mono tabular-nums whitespace-nowrap opacity-80">
                (${formatPrice(signal.entryRangeLow)} - ${formatPrice(signal.entryRangeHigh)})
              </span>
            )}
          </div>
        </div>

        {/* Targets grid */}
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-0.5">
            <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">
              Target
            </span>
            <p className="text-sm font-mono font-bold text-success tabular-nums truncate">
              ${formatPrice(signal.targetPrice)}
            </p>
          </div>
          <div className="space-y-0.5">
            <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">
              Stop
            </span>
            <p className="text-sm font-mono font-bold text-destructive tabular-nums truncate">
              ${formatPrice(signal.stopLoss)}
            </p>
          </div>
        </div>

        {/* Confidence meter */}
        <div className="space-y-1 pt-1">
          <div className="flex items-center justify-between">
            <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">
              AI Confidence
            </span>
            <span className="text-[10px] font-bold text-foreground tabular-nums">
              {displayConfidence}%
            </span>
          </div>
          <div className="h-1 w-full rounded-full bg-secondary">
            <div
              className={cn(
                'h-full rounded-full transition-all duration-500',
                displayConfidence >= 80 ? 'bg-success' : displayConfidence >= 60 ? 'bg-primary' : 'bg-warning'
              )}
              style={{ width: `${displayConfidence}%` }}
            />
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between border-t border-border/50 px-3 py-2 bg-secondary/5">
        <div className="flex items-center gap-1 text-[10px] text-muted-foreground font-medium">
          <Clock className="h-3 w-3" />
          <span>{timeAgo(signal.timestamp)}</span>
        </div>
        {signal.status === 'ACTIVE' && (
          <span className="flex items-center gap-1 text-[10px] font-bold text-success uppercase tracking-wider">
            <span className="relative flex h-1.5 w-1.5 ">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-75" />
              <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-success" />
            </span>
            Active
          </span>
        )}
      </div>
    </div>
  )
}
