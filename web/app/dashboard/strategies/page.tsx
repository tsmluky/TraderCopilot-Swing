'use client'

import { useState, useEffect, useMemo } from 'react'
import { toast } from 'sonner'
import { ConsolidatedStrategyCard, StrategyOffering } from '@/components/strategies/consolidated-strategy-card'
import { strategiesService } from '@/services/strategies'

export default function StrategiesPage() {
  const [offerings, setOfferings] = useState<StrategyOffering[]>([])
  const [lockedOfferings, setLockedOfferings] = useState<StrategyOffering[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchStrategies()
  }, [])

  const fetchStrategies = async () => {
    try {
      setIsLoading(true)
      const raw: any = await strategiesService.getMarketplace()

      if (raw && (raw.offerings || raw.locked_offerings)) {
        setOfferings(raw.offerings || [])
        setLockedOfferings(raw.locked_offerings || [])
      } else {
        console.warn("Unexpected API format", raw)
      }

    } catch (error) {
      console.error(error)
      toast.error('Failed to load strategies')
    } finally {
      setIsLoading(false)
    }
  }

  // Logic to group offerings by Strategy Code
  const strategyGroups = useMemo(() => {
    const allOfferings = [...offerings, ...lockedOfferings]
    const groups: Record<string, StrategyOffering[]> = {}

    allOfferings.forEach(offering => {
      if (!groups[offering.strategy_code]) {
        groups[offering.strategy_code] = []
      }
      groups[offering.strategy_code].push(offering)
    })

    return groups
  }, [offerings, lockedOfferings])

  const getStrategyDescription = (code: string) => {
    switch (code) {
      case 'TITAN_BREAKOUT':
      case 'donchian_v2':
      case 'DONCHIAN_BREAKOUT': return "Advanced volatility breakout system capitalizing on explosive market moves."

      case 'FLOW_MASTER':
      case 'trend_following_native_v1':
      case 'TREND_FOLLOWING': return "Momentum-based trend following engine designed for sustained directional moves."

      case 'MEAN_REVERSION':
      case 'mean_reversion_v1': return "Mean reversion scalp system for ranging markets."

      default: return "Automated trading system."
    }
  }

  return (
    <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-500">

      {/* Premium Header */}
      <div className="flex flex-col gap-3 pb-6 border-b border-border/40">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          Strategy Hub
        </h1>
        <p className="text-lg text-muted-foreground/80 font-light max-w-2xl">
          Explore and manage your active trading algorithms. Select different timeframes to view specific performance metrics and signal coverage.
        </p>
      </div>

      {isLoading ? (
        <div className="grid gap-8 grid-cols-1 md:grid-cols-2 xl:grid-cols-3 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-[400px] rounded-3xl bg-card/50 border border-border/50"></div>
          ))}
        </div>
      ) : (
        <div className="grid gap-6 grid-cols-1 md:grid-cols-2 xl:grid-cols-3">
          {Object.entries(strategyGroups).map(([code, variants]) => {
            const first = variants[0]
            return (
              <ConsolidatedStrategyCard
                key={code}
                strategyName={first.strategy_name}
                strategyCode={code}
                description={getStrategyDescription(code)}
                variants={variants}
              />
            )
          })}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && Object.keys(strategyGroups).length === 0 && (
        <div className="p-12 text-center text-muted-foreground border border-dashed border-border rounded-3xl bg-secondary/5">
          No strategies available at the moment.
        </div>
      )}
    </div>
  )
}