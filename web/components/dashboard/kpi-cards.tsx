import { Target, TrendingUp, TrendingDown, Activity, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface KPIData {
  winRate: number;
  avgReturn: number;
  maxDrawdown: number;
  last7dSignals: number;
  // Optional changes if backend provides them, otherwise we might hide or calculate
  winRateChange?: number;
  avgReturnChange?: number;
  drawdownChange?: number;
  signalsChange?: number;
}

interface KPICardsProps {
  data: KPIData;
  isLoading?: boolean;
}

export function KPICards({ data, isLoading }: KPICardsProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-32 rounded-xl border border-border/50 bg-card/50 animate-pulse" />
        ))}
      </div>
    )
  }

  const hasSignals = data.last7dSignals > 0;

  const kpis = [
    {
      label: 'Win Rate',
      value: hasSignals ? `${data.winRate}%` : '--',
      change: hasSignals && data.winRateChange ? `${data.winRateChange > 0 ? '+' : ''}${data.winRateChange}%` : '',
      changeDirection: (data.winRateChange || 0) >= 0 ? 'up' : 'down' as const,
      subtext: 'vs last 30 days',
      icon: Target,
      color: 'success' as const,
    },
    {
      label: 'Avg Return',
      value: hasSignals ? `${data.avgReturn > 0 ? '+' : ''}${data.avgReturn}%` : '--',
      change: hasSignals && data.avgReturnChange ? `${data.avgReturnChange}%` : '',
      changeDirection: (data.avgReturnChange || 0) >= 0 ? 'up' : 'down' as const,
      subtext: 'per signal',
      icon: TrendingUp,
      color: 'success' as const,
    },
    {
      label: 'PnL (7d)', // Adjusted label potentially
      value: hasSignals ? `$${data.avgReturn}` : '--', // We might map PnL here instead of avg return if desired, but sticking to prop mapping
      change: '',
      changeDirection: 'down' as const,
      subtext: 'risk metric',
      icon: TrendingDown,
      color: 'warning' as const,
    },
    {
      label: 'Signals (7d)',
      value: data.last7dSignals.toString(),
      change: hasSignals && data.signalsChange ? `${data.signalsChange}` : '',
      changeDirection: (data.signalsChange || 0) >= 0 ? 'up' : 'down' as const,
      subtext: 'generated',
      icon: Activity,
      color: 'primary' as const,
    }
  ]
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {kpis.map((kpi, index) => (
        <div
          key={kpi.label}
          className={cn(
            'group relative overflow-hidden rounded-xl border border-border/50 bg-card p-5 transition-all duration-300',
            'hover:border-border hover:shadow-soft-md',
            'animate-fade-up'
          )}
          style={{ animationDelay: `${index * 50}ms` }}
        >
          {/* Subtle gradient overlay on hover */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary/[0.02] to-transparent opacity-0 transition-opacity group-hover:opacity-100" />

          <div className="relative">
            {/* Header: Label + Icon */}
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                {kpi.label}
              </span>
              <div
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-lg transition-colors',
                  kpi.color === 'success' && 'bg-success-muted text-success',
                  kpi.color === 'warning' && 'bg-warning-muted text-warning',
                  kpi.color === 'primary' && 'bg-primary/10 text-primary'
                )}
              >
                <kpi.icon className="h-4 w-4" />
              </div>
            </div>

            {/* Value */}
            <div className="flex items-baseline gap-2 mb-1">
              <span
                className={cn(
                  'text-2xl font-semibold tracking-tight tabular-nums',
                  kpi.color === 'success' && 'text-success',
                  kpi.color === 'warning' && 'text-warning',
                  kpi.color === 'primary' && 'text-foreground'
                )}
              >
                {kpi.value}
              </span>

              {/* Change indicator */}
              <span
                className={cn(
                  'flex items-center gap-0.5 text-xs font-medium',
                  kpi.changeDirection === 'up' ? 'text-success' : 'text-destructive'
                )}
              >
                {kpi.changeDirection === 'up' ? (
                  <ArrowUpRight className="h-3 w-3" />
                ) : (
                  <ArrowDownRight className="h-3 w-3" />
                )}
                {kpi.change}
              </span>
            </div>

            {/* Subtext */}
            <p className="text-xs text-muted-foreground">{kpi.subtext}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
