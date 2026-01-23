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
    <div className="space-y-6">
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
      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
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
          {canAccessTelegram() ? (
            <Card className="bg-card/80 backdrop-blur-sm border-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Send className="h-4 w-4 text-primary" />
                  Telegram Alerts
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Status</span>
                  <Badge variant="outline" className="bg-success/10 text-success border-success/30 text-xs">
                    Connected
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Alerts sent</span>
                  <span className="text-sm font-medium text-foreground">--</span>
                </div>
                <p className="text-xs text-muted-foreground pt-2 border-t border-border">
                  You will receive instant alerts for all new signals matching your preferences.
                </p>
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
          <Card className="bg-card/80 backdrop-blur-sm border-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Bell className="h-4 w-4 text-primary" />
                Today's Activity
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">New signals</span>
                <span className="text-sm font-medium text-foreground">{stats.last7dSignals}</span>
              </div>
            </CardContent>
          </Card>

          {/* Gating Restrictions Info - Hide for PRO */}
          {(!user || user.plan !== 'PRO') && (
            <Card className="bg-card/50 border-border border-dashed">
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
