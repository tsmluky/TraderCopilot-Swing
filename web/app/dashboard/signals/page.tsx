'use client'

import { useState, useEffect } from 'react'
import { ArrowUpRight, ArrowDownRight, CheckCircle, XCircle, Clock, Filter, Lock, Activity, Zap, TrendingUp, TrendingDown } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'
import { useUser } from '@/lib/user-context'
import { logsService } from '@/services/logs'
import type { Signal, Token, Timeframe } from '@/lib/types'
import { toast } from 'sonner'
import { TOKEN_INFO } from '@/lib/types'
import { ScanDialog } from '@/components/dashboard/scan-dialog'
import { ScanProDialog } from '@/components/dashboard/scan-pro-dialog'
import { AuthError } from '@/lib/api-client'

// Helpers
const formatPrice = (p: number) => p.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
const formatPercent = (p: number) => `${p > 0 ? '+' : ''}${p.toFixed(2)}%`
const timeAgo = (date: Date | string) => {
  const d = new Date(date)
  const now = new Date()
  const diff = Math.floor((now.getTime() - d.getTime()) / 1000)
  if (diff < 60) return 'Just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return d.toLocaleDateString()
}

function SignalRow({ signal, isLocked }: { signal: Signal; isLocked: boolean }) {
  const tokenKey = signal.token as keyof typeof TOKEN_INFO
  const tokenInfo = TOKEN_INFO[tokenKey] || { name: signal.token, color: '#888' }
  const isLong = signal.type === 'LONG'
  const isClosed = signal.status === 'CLOSED'

  if (isLocked) {
    return (
      <TableRow className="border-b border-black/5 dark:border-white/5 opacity-60 hover:opacity-100 transition-opacity relative group/locked">
        <TableCell>
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-xl flex items-center justify-center bg-secondary/30 text-xs font-bold ring-1 ring-black/5 dark:ring-white/10 blur-[2px]">
              {signal.token}
            </div>
            <div className="flex flex-col blur-[3px]">
              <span className="font-bold text-sm">LOCKED</span>
              <span className="text-[10px] text-muted-foreground">PRO</span>
            </div>
          </div>
        </TableCell>
        <TableCell colSpan={6} className="text-center">
          <div className="absolute inset-0 flex items-center justify-center">
            <Badge variant="outline" className="gap-2 bg-white/80 dark:bg-black/50 backdrop-blur-md border-black/5 dark:border-white/10 text-muted-foreground group-hover/locked:bg-primary/5 group-hover/locked:dark:bg-primary/20 group-hover/locked:text-primary group-hover/locked:border-primary/20 transition-all cursor-not-allowed">
              <Lock className="w-3 h-3" /> Upgrade to View
            </Badge>
          </div>
        </TableCell>
      </TableRow>
    )
  }

  return (
    <TableRow className="border-b border-black/5 dark:border-white/5 hover:bg-black/5 dark:hover:bg-white/5 transition-colors group">
      <TableCell className="py-2.5">
        <div className="flex items-center gap-3">
          <div
            className="h-9 w-9 rounded-xl flex items-center justify-center text-[10px] font-black shadow-inner"
            style={{ backgroundColor: `${tokenInfo.color}15`, color: tokenInfo.color, border: `1px solid ${tokenInfo.color}30` }}
          >
            {signal.token}
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-sm text-foreground">{signal.token}</span>
            <span className="text-[10px] text-muted-foreground font-medium flex items-center gap-1">
              USDT <span className="w-1 h-1 rounded-full bg-muted-foreground/50" /> {signal.timeframe}
            </span>
          </div>
        </div>
      </TableCell>
      <TableCell>
        <Badge
          variant="outline"
          className={cn(
            'px-2.5 py-1 text-xs font-bold border-0 ring-1 ring-inset',
            isLong
              ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-500 ring-emerald-500/20'
              : 'bg-rose-500/10 text-rose-600 dark:text-rose-500 ring-rose-500/20'
          )}
        >
          {isLong ? <ArrowUpRight className="h-3 w-3 mr-1.5" /> : <ArrowDownRight className="h-3 w-3 mr-1.5" />}
          {signal.type}
        </Badge>
      </TableCell>
      <TableCell className="font-mono text-sm tracking-tight text-foreground/80">{formatPrice(signal.entryPrice)}</TableCell>
      <TableCell className="font-mono text-sm tracking-tight text-emerald-600 dark:text-emerald-500">{formatPrice(signal.targetPrice)}</TableCell>
      <TableCell className="font-mono text-sm tracking-tight text-rose-600/70 dark:text-rose-500/70">{formatPrice(signal.stopLoss)}</TableCell>
      <TableCell>
        {isClosed ? (
          <div className={cn(
            "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border",
            signal.pnl !== undefined && signal.pnl >= 0
              ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-500"
              : "bg-rose-500/10 border-rose-500/20 text-rose-600 dark:text-rose-500"
          )}>
            {signal.pnl !== undefined && signal.pnl >= 0 ? (
              <CheckCircle className="h-3.5 w-3.5" />
            ) : (
              <XCircle className="h-3.5 w-3.5" />
            )}
            {signal.pnl !== undefined ? formatPercent(signal.pnl) : '-'}
          </div>
        ) : (
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-600 dark:text-blue-500 text-xs font-bold animate-pulse">
            <Activity className="h-3.5 w-3.5" />
            Active
          </div>
        )}
      </TableCell>
      <TableCell className="text-muted-foreground text-xs font-medium">{timeAgo(signal.timestamp)}</TableCell>
    </TableRow>
  )
}

function StatCard({ label, value, icon: Icon, colorClass, subtext }: { label: string, value: string | number, icon: any, colorClass: string, subtext?: string }) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-black/5 dark:border-white/5 bg-white dark:bg-card/40 backdrop-blur-md p-3 group hover:border-black/10 dark:hover:border-white/10 transition-all duration-300 shadow-sm dark:shadow-none hover:shadow-lg dark:hover:shadow-none">
      <div className={cn("absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity mix-blend-multiply dark:mix-blend-normal", colorClass)} />
      <div className="relative z-10">
        <div className="flex items-center gap-2 mb-2">
          <div className="p-1.5 rounded-lg bg-black/5 dark:bg-white/5 text-muted-foreground group-hover:text-foreground transition-colors">
            <Icon className="w-4 h-4" />
          </div>
          <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">{label}</span>
        </div>
        <div className="text-2xl font-black text-foreground tabular-nums tracking-tight">
          {value}
        </div>
        {subtext && <p className="text-xs text-muted-foreground/60 mt-1">{subtext}</p>}
      </div>
    </div>
  )
}

export default function SignalsPage() {
  const { canAccessToken, canAccessTimeframe } = useUser()

  const [activeTab, setActiveTab] = useState('active')
  const [signals, setSignals] = useState<Signal[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [mounted, setMounted] = useState(false)

  const [filterToken, setFilterToken] = useState<string>('ALL')
  const [filterType, setFilterType] = useState<string>('ALL')

  useEffect(() => {
    setMounted(true)
    fetchSignals()
  }, [])

  const fetchSignals = async () => {
    try {
      setIsLoading(true)
      const data = await logsService.getRecentLogs({ include_system: false, limit: 100 })
      const list = Array.isArray(data) ? data : (data.logs || [])

      // TEST SIGNAL INJECTION
      const testSignal: any = {
        id: 'test-1',
        token: 'BTC',
        type: 'LONG',
        timeframe: '4H',
        entryPrice: 96500,
        targetPrice: 102000,
        stopLoss: 94000,
        status: 'ACTIVE',
        timestamp: new Date().toISOString(),
        confidence: 85,
        rationale: "Strong breakout above resistance with high volume."
      }

      // If list is empty or just to show it, we append it
      setSignals([testSignal, ...list])
    } catch (e) {
      console.error(e)
      toast.error("Failed to load signals")
    } finally {
      setIsLoading(false)
    }
  }

  const checkSignalAccess = (signal: Signal) => {
    return canAccessToken(signal.token as Token) && canAccessTimeframe(signal.timeframe as Timeframe)
  }

  const filteredSignals = signals.filter(s => {
    if (filterToken !== 'ALL' && s.token !== filterToken) return false
    if (filterType !== 'ALL' && s.type !== filterType) return false
    return true
  })

  const activeSignals = filteredSignals.filter((s) => s.status === 'ACTIVE' && s.type !== 'NEUTRAL')
  const closedSignals = filteredSignals.filter((s) => s.status === 'CLOSED' || s.type === 'NEUTRAL')

  // Stats
  const totalClosed = closedSignals.length
  const wins = closedSignals.filter((s) => s.pnl !== undefined && s.pnl > 0).length
  const totalPnl = closedSignals.reduce((acc, s) => acc + (s.pnl || 0), 0)

  if (!mounted) return null

  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">

      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-black/5 dark:border-white/5">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            Signal Terminal
          </h1>
          <p className="text-lg text-muted-foreground/80 font-light max-w-2xl">
            Real-time feed of institutional-grade swing setups.
          </p>
        </div>

        {/* Actions Area */}
        <div className="flex items-center gap-3">
          <div className="flex gap-2">
            <ScanDialog onScanComplete={fetchSignals} />
            <ScanProDialog onScanComplete={() => { }} />
          </div>

          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" className="gap-2 bg-black/5 dark:bg-black/20 border-black/5 dark:border-white/10 hover:bg-black/10 dark:hover:bg-white/5 hover:border-black/10 dark:hover:border-white/20 h-10 px-4">
                <Filter className="h-4 w-4" />
                Filter
                {(filterToken !== 'ALL' || filterType !== 'ALL') && (
                  <span className="flex h-2 w-2 rounded-full bg-primary shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-64 p-4 rounded-xl border-black/5 dark:border-white/10 bg-white/95 dark:bg-black/90 backdrop-blur-xl" align="end">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Asset</Label>
                  <Select value={filterToken} onValueChange={setFilterToken}>
                    <SelectTrigger className="h-9 bg-black/5 dark:bg-white/5 border-black/5 dark:border-white/10">
                      <SelectValue placeholder="All" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ALL">All Tokens</SelectItem>
                      {Object.keys(TOKEN_INFO).map(t => (
                        <SelectItem key={t} value={t}>{t}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Direction</Label>
                  <Select value={filterType} onValueChange={setFilterType}>
                    <SelectTrigger className="h-9 bg-black/5 dark:bg-white/5 border-black/5 dark:border-white/10">
                      <SelectValue placeholder="All" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ALL">All Types</SelectItem>
                      <SelectItem value="LONG">Long</SelectItem>
                      <SelectItem value="SHORT">Short</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {(filterToken !== 'ALL' || filterType !== 'ALL') && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full h-8 text-xs text-muted-foreground hover:text-foreground hover:bg-black/5 dark:hover:bg-white/5"
                    onClick={() => { setFilterToken('ALL'); setFilterType('ALL'); }}
                  >
                    Reset Filters
                  </Button>
                )}
              </div>
            </PopoverContent>
          </Popover>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid gap-4 sm:grid-cols-4">
        <StatCard
          label="Active Positions"
          value={activeSignals.length}
          icon={Activity}
          colorClass="from-blue-500/10 to-indigo-500/10"
          subtext="Live market opportunities"
        />
        <StatCard
          label="Signals Closed"
          value={totalClosed}
          icon={CheckCircle}
          colorClass="from-zinc-500/10 to-zinc-500/5"
          subtext="Historical performance"
        />
        <StatCard
          label="Win Rate"
          value={`${totalClosed > 0 ? ((wins / totalClosed) * 100).toFixed(0) : 0}%`}
          icon={Zap}
          colorClass="from-emerald-500/10 to-teal-500/10"
          subtext="Accuracy metric"
        />
        <StatCard
          label="Net P&L"
          value={formatPercent(totalPnl)}
          icon={totalPnl >= 0 ? TrendingUp : TrendingDown}
          colorClass={totalPnl >= 0 ? "from-emerald-500/10 to-emerald-500/5" : "from-rose-500/10 to-rose-500/5"}
          subtext="Cumulative return"
        />
      </div>

      {/* Signals Table */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full space-y-6">
        <div className="flex items-center justify-between">
          <TabsList className="bg-black/5 dark:bg-black/20 backdrop-blur-md border border-black/5 dark:border-white/5 p-1 rounded-xl h-auto">
            <TabsTrigger value="active" className="rounded-lg px-4 py-2 text-xs font-bold uppercase tracking-wider data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-lg shadow-primary/20 transition-all">
              Live Feed <Badge variant="secondary" className="ml-2 bg-white/20 text-white border-0">{activeSignals.length}</Badge>
            </TabsTrigger>
            <TabsTrigger value="closed" className="rounded-lg px-4 py-2 text-xs font-bold uppercase tracking-wider data-[state=active]:bg-white/80 dark:data-[state=active]:bg-white/10 data-[state=active]:text-foreground dark:data-[state=active]:text-white data-[state=active]:shadow-lg shadow-black/10 transition-all">
              History Archive <span className="ml-2 opacity-50">{closedSignals.length}</span>
            </TabsTrigger>
          </TabsList>
        </div>

        <Card className="bg-white dark:bg-card/40 backdrop-blur-xl border-black/5 dark:border-white/5 overflow-hidden rounded-3xl shadow-sm dark:shadow-none">
          <CardContent className="p-0">
            <TabsContent value="active" className="m-0">
              <Table>
                <TableHeader className="bg-black/5 dark:bg-black/20 border-b border-black/5 dark:border-white/5">
                  <TableRow className="hover:bg-transparent border-0">
                    <TableHead className="text-xs font-bold text-muted-foreground uppercase tracking-widest pl-6 h-12">Asset</TableHead>
                    <TableHead className="text-xs font-bold text-muted-foreground uppercase tracking-widest h-12">Direction</TableHead>
                    <TableHead className="text-xs font-bold text-muted-foreground uppercase tracking-widest h-12">Entry</TableHead>
                    <TableHead className="text-xs font-bold text-muted-foreground uppercase tracking-widest h-12">Target</TableHead>
                    <TableHead className="text-xs font-bold text-muted-foreground uppercase tracking-widest h-12">Stop</TableHead>
                    <TableHead className="text-xs font-bold text-muted-foreground uppercase tracking-widest h-12">Status</TableHead>
                    <TableHead className="text-xs font-bold text-muted-foreground uppercase tracking-widest h-12">Time</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {activeSignals.length === 0 ? (
                    <TableRow className="hover:bg-transparent">
                      <TableCell colSpan={7} className="text-center py-20">
                        <div className="flex flex-col items-center gap-3">
                          <div className="p-4 rounded-full bg-black/5 dark:bg-white/5 text-muted-foreground">
                            <Activity className="w-8 h-8 opacity-50" />
                          </div>
                          <p className="text-lg font-medium text-foreground">No active signals</p>
                          <p className="text-sm text-muted-foreground max-w-sm mx-auto">
                            The AI hasn't detected any high-probability setups at the moment. Try running a manual scan.
                          </p>
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    activeSignals.map((signal) => (
                      <SignalRow
                        key={signal.id}
                        signal={signal}
                        isLocked={!checkSignalAccess(signal)}
                      />
                    ))
                  )}
                </TableBody>
              </Table>
            </TabsContent>
            <TabsContent value="closed" className="m-0">
              <Table>
                <TableHeader className="bg-black/5 dark:bg-black/20 border-b border-black/5 dark:border-white/5">
                  <TableRow className="hover:bg-transparent border-0">
                    <TableHead className="text-xs font-bold text-muted-foreground uppercase tracking-widest pl-6 h-12">Asset</TableHead>
                    <TableHead className="text-xs font-bold text-muted-foreground uppercase tracking-widest h-12">Direction</TableHead>
                    <TableHead className="text-xs font-bold text-muted-foreground uppercase tracking-widest h-12">Entry</TableHead>
                    <TableHead className="text-xs font-bold text-muted-foreground uppercase tracking-widest h-12">Target</TableHead>
                    <TableHead className="text-xs font-bold text-muted-foreground uppercase tracking-widest h-12">Stop</TableHead>
                    <TableHead className="text-xs font-bold text-muted-foreground uppercase tracking-widest h-12">Result</TableHead>
                    <TableHead className="text-xs font-bold text-muted-foreground uppercase tracking-widest h-12">Closed</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {closedSignals.map((signal) => (
                    <SignalRow
                      key={signal.id}
                      signal={signal}
                      isLocked={!checkSignalAccess(signal)}
                    />
                  ))}
                </TableBody>
              </Table>
            </TabsContent>
          </CardContent>
        </Card>
      </Tabs>
    </div>
  )
}
