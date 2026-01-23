'use client'

import { useState, useEffect } from 'react'
import { toast } from 'sonner'
import { Search, SlidersHorizontal } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { MasterStrategyCard } from '@/components/strategies/master-strategy-card'
import { strategiesService } from '@/services/strategies'
import type { Strategy } from '@/lib/types'

export default function StrategiesPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [togglingId, setTogglingId] = useState<string | null>(null)

  useEffect(() => {
    fetchStrategies()
  }, [])

  const fetchStrategies = async (showLoading = true) => {
    try {
      if (showLoading) setIsLoading(true)
      const list = await strategiesService.getMarketplace()
      setStrategies(list)
    } catch (error) {
      console.error(error)
      toast.error('Failed to load strategies')
    } finally {
      if (showLoading) setIsLoading(false)
    }
  }

  // Restore robust toggle handler
  const handleToggle = async (id: string, targetStatus: boolean, newTimeframe?: string) => {
    try {
      setTogglingId(id)

      // If switching timeframe first
      if (newTimeframe) {
        await strategiesService.updatePersona(id, { timeframe: newTimeframe })
      }

      // We rely on backend response or strict status
      await strategiesService.togglePersona(id)

      if (newTimeframe) {
        // If timeframe changed, full refetch is safest to ensure 'isContextActive' checks in Cards are correct
        await fetchStrategies(false)
      } else {
        // Optimistic update
        setStrategies(prev => prev.map(s =>
          s.id === id ? { ...s, isActive: targetStatus } : s
        ))
      }

      toast.success(`Strategy ${targetStatus ? 'enabled' : 'disabled'}`)
    } catch (error) {
      console.error(error)
      toast.error('Failed to update strategy')
    } finally {
      setTogglingId(null)
    }
  }

  // Group helpers
  const groupByName = (list: Strategy[]) => {
    return list.reduce((acc, strat) => {
      if (!acc[strat.name]) acc[strat.name] = []
      acc[strat.name].push(strat)
      return acc
    }, {} as Record<string, Strategy[]>)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Strategies</h1>
          <p className="text-muted-foreground">
            Explore our proven swing trading strategies
          </p>
        </div>
      </div>

      {/* Strategy Grid */}
      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2 animate-pulse">
          <div className="h-64 rounded-xl bg-card/50 border border-border/50"></div>
          <div className="h-64 rounded-xl bg-card/50 border border-border/50"></div>
        </div>
      ) : (
        <Accordion type="multiple" defaultValue={['4h']} className="space-y-6">

          {/* 4H Section - Swing */}
          <AccordionItem value="4h" className="border-none bg-transparent">
            <AccordionTrigger className="px-1 hover:no-underline py-2">
              <div className="flex items-center gap-2">
                <span className="flex h-2 w-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></span>
                <h2 className="text-lg font-semibold text-foreground">Swing Strategies (4H)</h2>
                <span className="ml-2 text-[10px] text-muted-foreground uppercase tracking-wider font-medium bg-secondary/50 px-2 py-0.5 rounded border border-border/50">
                  Recommended
                </span>
              </div>
            </AccordionTrigger>
            <AccordionContent className="pt-4 pb-2">
              <div className="grid gap-6 md:grid-cols-2">
                {Object.entries(groupByName(strategies.filter(s => s.timeframes?.some(t => t.toLowerCase() === '4h')))).map(([name, persons]) => (
                  <MasterStrategyCard
                    key={`4h-${name}`}
                    name={name}
                    personas={persons}
                    onToggle={handleToggle}
                    isToggling={typeof togglingId === 'string'}
                    onRefresh={() => fetchStrategies(false)}
                    forcedTimeframe="4h"
                  />
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* 1D Section - Daily */}
          <AccordionItem value="1d" className="border-none bg-transparent">
            <AccordionTrigger className="px-1 hover:no-underline py-2">
              <div className="flex items-center gap-2">
                <span className="flex h-2 w-2 rounded-full bg-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.5)]"></span>
                <h2 className="text-lg font-semibold text-foreground">Daily Trend (1D)</h2>
              </div>
            </AccordionTrigger>
            <AccordionContent className="pt-4 pb-2">
              <div className="grid gap-6 md:grid-cols-2">
                {Object.entries(groupByName(strategies.filter(s => s.timeframes?.some(t => t.toLowerCase() === '1d')))).map(([name, persons]) => (
                  <MasterStrategyCard
                    key={`1d-${name}`}
                    name={name}
                    personas={persons}
                    onToggle={handleToggle}
                    isToggling={typeof togglingId === 'string'}
                    onRefresh={() => fetchStrategies(false)}
                    forcedTimeframe="1d"
                  />
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>

          {/* 1H Section - Pro */}
          <AccordionItem value="1h" className="border-none bg-transparent">
            <AccordionTrigger className="px-1 hover:no-underline py-2">
              <div className="flex items-center gap-2">
                <span className="flex h-2 w-2 rounded-full bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.5)]"></span>
                <h2 className="text-lg font-semibold text-foreground">Scalping Pro (1H)</h2>
                <Badge variant="outline" className="ml-2 border-orange-500/20 text-orange-500 bg-orange-500/10 text-[10px]">PRO</Badge>
              </div>
            </AccordionTrigger>
            <AccordionContent className="pt-4 pb-2">
              <div className="grid gap-6 md:grid-cols-2">
                {Object.entries(groupByName(strategies.filter(s => s.timeframes?.some(t => t.toLowerCase() === '1h')))).map(([name, persons]) => (
                  <MasterStrategyCard
                    key={`1h-${name}`}
                    name={name}
                    personas={persons}
                    onToggle={handleToggle}
                    isToggling={typeof togglingId === 'string'}
                    onRefresh={() => fetchStrategies(false)}
                    forcedTimeframe="1h"
                  />
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      )}

      {/* Info Section */}
      <div className="rounded-lg border border-border bg-card/50 p-6">
        <h3 className="font-medium text-foreground mb-2">How Strategies Work</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Each strategy uses a combination of technical indicators and price action analysis
          optimized for swing trading timeframes (1H, 4H, 1D). Signals are generated
          automatically when all strategy conditions are met. Historical performance
          is calculated using backtested and live signal data.
        </p>
      </div>
    </div>
  )
}