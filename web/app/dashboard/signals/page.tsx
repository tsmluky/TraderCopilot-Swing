'use client'

import { useState, useEffect } from 'react'
import { ArrowUpRight, ArrowDownRight, CheckCircle, XCircle, Clock, Filter, Lock } from 'lucide-react'
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
      <TableRow className="opacity-50">
        <TableCell>
          <div className="flex items-center gap-2">
            <div
              className="h-6 w-6 rounded-full flex items-center justify-center text-[10px] font-bold"
              style={{ backgroundColor: `${tokenInfo.color}20`, color: tokenInfo.color }}
            >
              {signal.token}
            </div>
            <span className="font-medium text-foreground">{signal.token}/USDT</span>
          </div>
        </TableCell>
        <TableCell colSpan={6} className="text-center text-muted-foreground">
          <Badge variant="outline" className="text-xs gap-1 border-yellow-500/50 text-yellow-500">
            <Lock className="w-3 h-3" /> Locked
          </Badge>
        </TableCell>
      </TableRow>
    )
  }

  return (
    <TableRow className="hover:bg-secondary/30">
      <TableCell>
        <div className="flex items-center gap-2">
          <div
            className="h-6 w-6 rounded-full flex items-center justify-center text-[10px] font-bold"
            style={{ backgroundColor: `${tokenInfo.color}20`, color: tokenInfo.color }}
          >
            {signal.token}
          </div>
          <span className="font-medium text-foreground">{signal.token}/USDT</span>
        </div>
      </TableCell>
      <TableCell>
        <Badge
          variant="outline"
          className={cn(
            'text-xs',
            isLong ? 'border-success/30 text-success' : 'border-destructive/30 text-destructive'
          )}
        >
          {isLong ? <ArrowUpRight className="h-3 w-3 mr-1" /> : <ArrowDownRight className="h-3 w-3 mr-1" />}
          {signal.type}
        </Badge>
      </TableCell>
      <TableCell className="font-mono text-sm">{formatPrice(signal.entryPrice)}</TableCell>
      <TableCell className="font-mono text-sm text-success">{formatPrice(signal.targetPrice)}</TableCell>
      <TableCell className="font-mono text-sm text-destructive">{formatPrice(signal.stopLoss)}</TableCell>
      <TableCell>
        <Badge variant="secondary" className="text-xs">{signal.timeframe}</Badge>
      </TableCell>
      <TableCell>
        {isClosed ? (
          <div className="flex items-center gap-1">
            {signal.pnl !== undefined && signal.pnl >= 0 ? (
              <CheckCircle className="h-4 w-4 text-success" />
            ) : (
              <XCircle className="h-4 w-4 text-destructive" />
            )}
            <span
              className={cn(
                'font-medium text-sm',
                signal.pnl !== undefined && signal.pnl >= 0 ? 'text-success' : 'text-destructive'
              )}
            >
              {signal.pnl !== undefined ? formatPercent(signal.pnl) : '-'}
            </span>
          </div>
        ) : (
          <Badge variant="outline" className="text-xs border-primary/30 text-primary">
            <Clock className="h-3 w-3 mr-1" />
            Active
          </Badge>
        )}
      </TableCell>
      <TableCell className="text-muted-foreground text-xs">{timeAgo(signal.timestamp)}</TableCell>
    </TableRow>
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
      setSignals(list)
    } catch (e) {
      // if (e instanceof AuthError) return // Handled by AuthContext // useUser doesn't throw AuthError directly usually
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

  // Stats (calculated from ALL signals or filtered? Usually filtered to reflect view)
  const totalClosed = closedSignals.length
  const wins = closedSignals.filter((s) => s.pnl !== undefined && s.pnl > 0).length
  const totalPnl = closedSignals.reduce((acc, s) => acc + (s.pnl || 0), 0)



  if (!mounted) return null

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Signal History</h1>
          <p className="text-muted-foreground">
            Track active signals and review past performance
          </p>
        </div>
        <div className="flex items-center gap-2">
          <ScanDialog onScanComplete={fetchSignals} />
          <ScanProDialog onScanComplete={() => { }} />

          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" className="gap-2 bg-transparent">
                <Filter className="h-4 w-4" />
                Filter
                {(filterToken !== 'ALL' || filterType !== 'ALL') && (
                  <span className="flex h-2 w-2 rounded-full bg-primary" />
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-56 p-3" align="end">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-xs font-medium text-muted-foreground uppercase">Token</Label>
                  <Select value={filterToken} onValueChange={setFilterToken}>
                    <SelectTrigger className="h-8">
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
                  <Label className="text-xs font-medium text-muted-foreground uppercase">Type</Label>
                  <Select value={filterType} onValueChange={setFilterType}>
                    <SelectTrigger className="h-8">
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
                    className="w-full h-8 text-xs text-muted-foreground hover:text-foreground"
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

      {/* Stats Cards */}
      <div className="grid gap-4 sm:grid-cols-4">
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">Active</p>
            <p className="text-2xl font-semibold text-primary">{activeSignals.length}</p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">Closed</p>
            <p className="text-2xl font-semibold text-foreground">{totalClosed}</p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">Win Rate</p>
            <p className="text-2xl font-semibold text-success">
              {totalClosed > 0 ? ((wins / totalClosed) * 100).toFixed(0) : 0}%
            </p>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">Total P&L</p>
            <p className={cn('text-2xl font-semibold', totalPnl >= 0 ? 'text-success' : 'text-destructive')}>
              {formatPercent(totalPnl)}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Signals Table */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <Card className="bg-card border-border">
          <CardHeader className="pb-0">
            <TabsList className="bg-secondary/50">
              <TabsTrigger value="active">
                Active ({activeSignals.length})
              </TabsTrigger>
              <TabsTrigger value="closed">
                History ({closedSignals.length})
              </TabsTrigger>
            </TabsList>
          </CardHeader>
          <CardContent className="p-0">
            <TabsContent value="active" className="m-0">
              <Table>
                <TableHeader>
                  <TableRow className="border-border hover:bg-transparent">
                    <TableHead className="text-muted-foreground">Token</TableHead>
                    <TableHead className="text-muted-foreground">Type</TableHead>
                    <TableHead className="text-muted-foreground">Entry</TableHead>
                    <TableHead className="text-muted-foreground">Target</TableHead>
                    <TableHead className="text-muted-foreground">Stop Loss</TableHead>
                    <TableHead className="text-muted-foreground">TF</TableHead>
                    <TableHead className="text-muted-foreground">Status</TableHead>
                    <TableHead className="text-muted-foreground">Time</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {activeSignals.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                        No active signals. Try running a scan!
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
                <TableHeader>
                  <TableRow className="border-border hover:bg-transparent">
                    <TableHead className="text-muted-foreground">Token</TableHead>
                    <TableHead className="text-muted-foreground">Type</TableHead>
                    <TableHead className="text-muted-foreground">Entry</TableHead>
                    <TableHead className="text-muted-foreground">Target</TableHead>
                    <TableHead className="text-muted-foreground">Stop Loss</TableHead>
                    <TableHead className="text-muted-foreground">TF</TableHead>
                    <TableHead className="text-muted-foreground">Result</TableHead>
                    <TableHead className="text-muted-foreground">Time</TableHead>
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
