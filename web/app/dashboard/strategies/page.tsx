'use client'

import { useState, useEffect, useMemo } from 'react'
import { toast } from 'sonner'
import { StrategyStackModule, StrategyOffering } from '@/components/strategies/strategy-stack-module'
import { strategiesService } from '@/services/strategies'

export default function StrategiesPage() {
  const [offerings, setOfferings] = useState<StrategyOffering[]>([])
  const [lockedOfferings, setLockedOfferings] = useState<StrategyOffering[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // User Preferences
  const [disabledStrategies, setDisabledStrategies] = useState<string[]>([])

  useEffect(() => {
    fetchStrategies()
    fetchPreferences()
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

  const fetchPreferences = async () => {
    try {
      const disabled = await strategiesService.getPreferences()
      setDisabledStrategies(disabled || [])
    } catch (err) {
      console.error("Failed to load preferences", err)
    }
  }

  const toggleStrategy = async (code: string, enabled: boolean) => {
    // Optimistic update
    const prev = [...disabledStrategies]
    let next: string[]

    if (enabled) {
      // Check: enabled means "Remove from disabled list"
      next = prev.filter(c => c !== code)
      toast.success(`${getStrategyName(code)} activated`)
    } else {
      // Check: disabled means "Add to disabled list"
      if (!prev.includes(code)) {
        next = [...prev, code]
      } else {
        next = prev
      }
      toast.message(`${getStrategyName(code)} deactivated`)
    }

    setDisabledStrategies(next)

    try {
      await strategiesService.updatePreferences(next)
    } catch (err) {
      // Revert
      setDisabledStrategies(prev)
      toast.error("Failed to update preference")
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
      case 'DONCHIAN_V2': return "Advanced volatility breakout system capitalizing on explosive market moves."

      case 'FLOW_MASTER':
      case 'trend_following_native_v1':
      case 'SMA_CROSSOVER': return "Optimized SMA Crossover engine designed for sustained directional moves."

      case 'SUPER_TREND':
      case 'supertrend_v1': return "Volatility-based trend following using ATR trailing stops."

      case 'MEAN_REVERSION':
      case 'MEAN_REVERSION_V1':
      case 'mean_reversion_v1': return "Mean reversion scalp system for ranging markets."

      default: return "Automated trading system."
    }
  }

  const getStrategyName = (code: string) => {
    switch (code) {
      case 'TITAN_BREAKOUT':
      case 'donchian_v2':
      case 'DONCHIAN_V2': return "Donchian Breakout"

      case 'FLOW_MASTER':
      case 'trend_following_native_v1':
      case 'SMA_CROSSOVER': return "Trend Surfer (SMA)"

      case 'SUPER_TREND':
      case 'supertrend_v1': return "SuperTrend"

      case 'MEAN_REVERSION':
      case 'MEAN_REVERSION_V1':
      case 'mean_reversion_v1': return "Mean Reversion"

      default: return "Strategy"
    }
  }

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-5xl mx-auto">

      {/* Premium Header */}
      <div className="flex flex-col gap-2 pb-8 pt-4">
        <h1 className="text-3xl font-black tracking-tighter text-foreground flex items-center gap-3">
          <span className="text-zinc-600">CORTEX</span> / MODULES
        </h1>
        <p className="text-base text-zinc-500 font-medium max-w-2xl">
          Manage the active neural layers of your trading brain. Ignite modules to enable specific market analysis pathways.
        </p>
      </div>

      {isLoading ? (
        <div className="flex flex-col gap-4 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-[120px] w-full rounded-2xl bg-zinc-900/50 border border-zinc-800"></div>
          ))}
        </div>
      ) : (
        <div className="flex flex-col gap-2 relative">
          {/* Background spinal cord line */}
          <div className="absolute left-[27px] top-0 bottom-6 w-[2px] bg-zinc-900/50 -z-10" />

          {Object.entries(strategyGroups).map(([code, variants], idx, arr) => {
            const first = variants[0]
            const isEnabled = !disabledStrategies.includes(code)
            const isLast = idx === arr.length - 1

            // Normalize Strategy Name using our helper to ensure consistency
            const displayName = getStrategyName(code)

            return (
              <StrategyStackModule
                key={code}
                strategyName={displayName}
                strategyCode={code}
                description={getStrategyDescription(code)}
                variants={variants}
                isEnabled={isEnabled}
                onToggle={(val) => toggleStrategy(code, val)}
                isLast={isLast}
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