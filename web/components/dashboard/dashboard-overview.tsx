'use client'

import { useState, useEffect } from 'react'
import { Bell, Lock, Send } from 'lucide-react'
import { KPICards } from './kpi-cards'
import { SignalsFeed } from './signals-feed'
import { DashboardTopBar } from './dashboard-top-bar'
import { LockedFeatureCard } from '@/components/locked-feature-card'
import { useUser } from '@/lib/user-context'
import type { Token, Timeframe, Signal } from '@/lib/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { statsService } from '@/services/stats'
import { logsService } from '@/services/logs'

export function DashboardOverview() {
  const { canAccessTelegram, user } = useUser()
  const [selectedToken, setSelectedToken] = useState<Token | 'ALL'>('ALL')
  const [selectedTimeframe, setSelectedTimeframe] = useState<Timeframe | 'ALL'>('ALL')

  const [stats, setStats] = useState<any>({
    winRate: 0,
    avgReturn: 0,
    maxDrawdown: 0,
    last7dSignals: 0
  })
  const [signals, setSignals] = useState<Signal[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchData = async () => {
    setIsLoading(true)
    try {
      const [statsData, logsData] = await Promise.all([
        statsService.getDashboardStats(),
        logsService.getRecentLogs({ limit: 50, include_system: true })
      ])

      // Map Stats: Adapting backend summary to UI expectations
      // Backend: { summary: { total_signals, win_rate_24h, signals_generated_24h, ... } }
      const s = statsData.summary || {}
      setStats({
        winRate: s.win_rate_24h || 0,
        avgReturn: s.pnl_7d || 0,
        maxDrawdown: 0,
        last7dSignals: s.open_signals || 0
      })

      // Map Signals
      // logsData is List<LogEntry>
      const rawLogs = Array.isArray(logsData) ? logsData : (logsData.results || [])
      const mappedSignals: Signal[] = rawLogs
        .map((log: any) => ({
          id: (log.id || Math.random()).toString(),
          token: (log.token || 'BTC').toUpperCase(),
          timeframe: (log.timeframe || '4h').toUpperCase(),
          type: (log.direction || 'NEUTRAL').toUpperCase(),
          entryPrice: log.entry || 0,
          targetPrice: log.tp || 0,
          stopLoss: log.sl || 0,
          confidence: log.confidence || 0,
          timestamp: log.timestamp ? new Date(log.timestamp) : new Date(),
          status: log.status === 'OPEN' ? 'ACTIVE' : 'CLOSED',
          evaluation: log.status !== 'OPEN' ? 'evaluated' : 'pending',
          pnl: log.pnl,
          rationale: log.rationale
        }))
        .filter((s: Signal) => s.type !== 'NEUTRAL')

      // Test Signal Injection
      mappedSignals.unshift({
        id: 'test-sig-1',
        token: 'BTC',
        timeframe: '4H',
        type: 'LONG',
        entryPrice: 64200,
        targetPrice: 68500,
        stopLoss: 62500,
        confidence: 0.85,
        timestamp: new Date(),
        status: 'ACTIVE',
        evaluation: 'pending',
        pnl: undefined,
        rationale: "Bullish divergence on RSI + Support retest. Institutional flow detected."
      })

      setSignals(mappedSignals)

    } catch (e) {
      console.error("Dashboard fetch error", e)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <div className="space-y-4">
      {/* Top Bar with Selectors */}
      <DashboardTopBar
        selectedToken={selectedToken}
        selectedTimeframe={selectedTimeframe}
        onTokenChange={setSelectedToken}
        onTimeframeChange={setSelectedTimeframe}
      />

      {/* KPI Cards */}
      <KPICards data={stats} isLoading={isLoading} />

      {/* Main Content Grid */}
      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        {/* Signals Feed */}
        <SignalsFeed
          selectedToken={selectedToken}
          selectedTimeframe={selectedTimeframe}
          signals={signals}
          isLoading={isLoading}
          onRefresh={fetchData}
        />

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Telegram Status Card */}
          {/* Telegram Status Card */}
          {canAccessTelegram() ? (
            <Card className="bg-white dark:bg-card/40 backdrop-blur-xl border-black/5 dark:border-white/5 overflow-hidden group hover:border-primary/20 transition-all duration-500 shadow-sm dark:shadow-none">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-50" />
              <CardHeader className="pb-3 relative z-10 border-b border-black/5 dark:border-white/5">
                <CardTitle className="text-sm font-bold flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-primary/10 text-primary">
                    <Send className="h-4 w-4" />
                  </div>
                  Telegram Alerts
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 pt-4 relative z-10">
                <div className="flex items-center justify-between p-3 rounded-xl bg-black/5 dark:bg-black/20 border border-black/5 dark:border-white/5">
                  <span className="text-xs font-medium text-muted-foreground">Status</span>
                  <div className="flex items-center gap-2">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    <span className="text-xs font-bold text-emerald-600 dark:text-emerald-500">Active</span>
                  </div>
                </div>
                <div className="flex items-center justify-between px-1">
                  <span className="text-xs text-muted-foreground">Alerts delivered</span>
                  <span className="text-sm font-bold text-foreground">--</span>
                </div>
              </CardContent>
            </Card>
          ) : (
            <LockedFeatureCard
              title="Telegram Alerts"
              description="Get instant signal notifications directly to your Telegram."
              requiredPlan="TRADER"
              icon={<Send className="h-6 w-6 text-muted-foreground" />}
            />
          )}

          {/* Quick Stats */}
          <Card className="bg-white dark:bg-card/40 backdrop-blur-xl border-black/5 dark:border-white/5 overflow-hidden shadow-sm dark:shadow-none">
            <CardHeader className="pb-3 border-b border-black/5 dark:border-white/5">
              <CardTitle className="text-sm font-bold flex items-center gap-2">
                <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-500">
                  <Bell className="h-4 w-4" />
                </div>
                Today's Activity
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 pt-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">New signals</span>
                <span className="text-xl font-bold text-foreground">{stats.last7dSignals}</span>
              </div>
            </CardContent>
          </Card>

          {/* Gating Restrictions Info - Hide for PRO */}
          {(!user || user.plan !== 'PRO') && (
            <Card className="bg-white dark:bg-card/50 border-black/10 dark:border-border border-dashed shadow-sm dark:shadow-none">
              <CardContent className="p-4">
                <p className="text-xs text-muted-foreground leading-relaxed">
                  <span className="font-medium text-foreground">Plan restrictions: </span>
                  {canAccessTelegram() ? (
                    'You have full access to all tokens and 4H/1D timeframes. Upgrade to SwingPro for 1H signals and AI Advisor.'
                  ) : (
                    'Trial includes BTC & ETH only on 4H/1D. Upgrade for more tokens, Telegram alerts, and AI Advisor.'
                  )}
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
