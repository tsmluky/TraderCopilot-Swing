import { Target, TrendingUp, TrendingDown, Activity, ArrowUpRight, ArrowDownRight, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface KPIData {
  winRate: number;
  avgReturn: number;
  maxDrawdown: number;
  last7dSignals: number;
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
      <div className="grid grid-cols-2 gap-3 sm:gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-40 rounded-3xl border border-border/40 bg-card/20 animate-pulse" />
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
      theme: 'emerald'
    },
    {
      label: 'Avg Return',
      value: hasSignals ? `${data.avgReturn > 0 ? '+' : ''}${data.avgReturn}%` : '--',
      change: hasSignals && data.avgReturnChange ? `${data.avgReturnChange}%` : '',
      changeDirection: (data.avgReturnChange || 0) >= 0 ? 'up' : 'down' as const,
      subtext: 'per signal',
      icon: TrendingUp,
      theme: 'blue'
    },
    {
      label: 'Performance (7d)',
      value: hasSignals ? `+${data.avgReturn * data.last7dSignals}%` : '--', // Mocked estimation
      change: '',
      changeDirection: 'up' as const,
      subtext: 'estimated yield',
      icon: Zap,
      theme: 'orange'
    },
    {
      label: 'Total Signals',
      value: data.last7dSignals.toString(),
      change: hasSignals && data.signalsChange ? `${data.signalsChange}` : '',
      changeDirection: (data.signalsChange || 0) >= 0 ? 'up' : 'down' as const,
      subtext: 'last 7 days',
      icon: Activity,
      theme: 'purple'
    }
  ]

  const themes = {
    emerald: {
      bg: "from-emerald-500/10 to-teal-500/5",
      iconBg: "bg-emerald-500/20 text-emerald-500",
      text: "text-emerald-500",
      border: "group-hover:border-emerald-500/30"
    },
    blue: {
      bg: "from-blue-500/10 to-indigo-500/5",
      iconBg: "bg-blue-500/20 text-blue-500",
      text: "text-blue-500",
      border: "group-hover:border-blue-500/30"
    },
    orange: {
      bg: "from-orange-500/10 to-amber-500/5",
      iconBg: "bg-orange-500/20 text-orange-500",
      text: "text-orange-500",
      border: "group-hover:border-orange-500/30"
    },
    purple: {
      bg: "from-purple-500/10 to-pink-500/5",
      iconBg: "bg-purple-500/20 text-purple-500",
      text: "text-purple-500",
      border: "group-hover:border-purple-500/30"
    }
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {kpis.map((kpi, index) => {
        const theme = themes[kpi.theme as keyof typeof themes] || themes.blue
        return (
          <div
            key={kpi.label}
            className={cn(
              'group relative overflow-hidden rounded-3xl border border-black/5 dark:border-white/5 bg-white dark:bg-card/40 backdrop-blur-md p-4 transition-all duration-500 shadow-sm dark:shadow-none hover:shadow-md dark:hover:border-white/10',
              theme.border
            )}
            style={{ animationDelay: `${index * 100}ms` }}
          >
            {/* Background Gradient */}
            <div className={cn("absolute inset-0 bg-gradient-to-br opacity-30 dark:opacity-50 transition-opacity", theme.bg)} />

            <div className="relative z-10">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest">
                  {kpi.label}
                </span>
                <div className={cn("p-1.5 rounded-xl", theme.iconBg)}>
                  <kpi.icon className="h-4 w-4" />
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-black tracking-tight text-foreground tabular-nums">
                    {kpi.value}
                  </span>
                  {kpi.change && (
                    <span className={cn("flex items-center text-xs font-bold", kpi.changeDirection === 'up' ? 'text-emerald-600 dark:text-emerald-500' : 'text-rose-600 dark:text-rose-500')}>
                      {kpi.changeDirection === 'up' ? <ArrowUpRight className="h-3 w-3 mr-0.5" /> : <ArrowDownRight className="h-3 w-3 mr-0.5" />}
                      {kpi.change}
                    </span>
                  )}
                </div>
                <p className="text-xs font-medium text-muted-foreground/60">
                  {kpi.subtext}
                </p>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
