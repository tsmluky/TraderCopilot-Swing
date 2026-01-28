'use client'

import { useState, useMemo, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { CheckCircle2, TrendingUp, Activity, BarChart3, AlertTriangle, Lock, BookOpen, Ban, Lightbulb, Scale, Filter, Download, BadgeDollarSign } from "lucide-react"
import type { StrategyOffering } from "./master-strategy-card"
import { PERFORMANCE_HISTORY, PerformanceMetric } from "@/data/performance_history"
import verifiedStats from '@/data/verification_stats.json'
import { cn } from "@/lib/utils"

interface StrategyDetailsModalProps {
    offering: StrategyOffering | null
    variants?: StrategyOffering[]
    open: boolean
    onOpenChange: (open: boolean) => void
}

export function StrategyDetailsModal({ offering, variants, open, onOpenChange }: StrategyDetailsModalProps) {
    const [perfPeriod, setPerfPeriod] = useState<"6m" | "2y" | "5y">("5y")
    const [activeTokens, setActiveTokens] = useState<Set<string>>(new Set()) // Multiselect for tokens
    const [activeTimeframes, setActiveTimeframes] = useState<Set<string>>(new Set()) // Multiselect for timeframes (1H, 4H)

    // Reset filters when modal opens or offering changes
    useEffect(() => {
        if (open && offering) {
            // Default: Activate all tokens available in this offering (or all unique ones from perf data)
            // But usually user wants to see what's in the offering first.
            // Let's activate ALL tokens by default.
            // And activate BOTH 1H and 4H if available (or just the current one + siblings).

            // For timeframes: enable all from the passed variants, or just 1H/4H if variants not passed (fallback)
            if (variants && variants.length > 0) {
                setActiveTimeframes(new Set(variants.map(v => v.timeframe)))
            } else {
                setActiveTimeframes(new Set([offering.timeframe]))
            }

            // For tokens: we'll set this after we fetch the data, or just default to "ALL" logic if set is empty?
            // Let's default to empty set = "Select All". It's easier UI logic: "If empty, show all".
            setActiveTokens(new Set())
        }
    }, [open, offering, variants])


    if (!offering) return null

    const details = getStrategyDetails(offering.strategy_code)

    // Resolve Performance ID Key
    let perfKey = offering.strategy_code
    if (offering.strategy_code === 'TITAN_BREAKOUT') perfKey = 'donchian_v2'
    if (offering.strategy_code === 'FLOW_MASTER') perfKey = 'trend_following_native_v1'
    if (offering.strategy_code === 'MEAN_REVERSION') perfKey = 'mean_reversion_v1'

    // Fetch Full Data Source
    const allPerfData = PERFORMANCE_HISTORY[perfKey] || []

    // Get Unique Lists for Filtering Controls
    const uniqueTokens = Array.from(new Set(allPerfData.map(d => d.token)))
    const uniqueTimeframes = Array.from(new Set(allPerfData.map(d => d.timeframe.toUpperCase()))) // Should contain 1H, 4H

    // --- FILTER & SCALING LOGIC ---
    const filteredData = useMemo(() => {
        return allPerfData
            .filter(d => {
                // Filter by Timeframe
                const tfMatch = activeTimeframes.size === 0 || activeTimeframes.has(d.timeframe.toUpperCase())
                // Filter by Token
                const tokenMatch = activeTokens.size === 0 || activeTokens.has(d.token)
                return tfMatch && tokenMatch
            })
            .map(d => {
                // APPLY PERIOD MULTIPLIERS (Simulation of historical slices)
                let mult = 1.0
                let wrAdjust = 0

                if (perfPeriod === '2y') {
                    mult = 0.4 // ~40% of trades
                    wrAdjust = -1.5 // Slightly lower winrate usually in bear market cycles
                } else if (perfPeriod === '6m') {
                    mult = 0.12 // ~10% of trades
                    wrAdjust = 2.5 // Recent performance might be better/worse
                }

                const scaledTrades = Math.floor(Math.max(d.total_trades * mult, 12)) // Minimum 12 trades
                const scaledWinRate = Math.min(Math.max(d.win_rate + wrAdjust, 30), 85) // Clamp 30-85%
                const scaledTotalR = Number((d.total_r * mult).toFixed(1))
                const scaledWins = Math.round(scaledTrades * (scaledWinRate / 100))
                const scaledLosses = scaledTrades - scaledWins

                return {
                    ...d,
                    total_trades: scaledTrades,
                    win_rate: Number(scaledWinRate.toFixed(1)),
                    total_r: scaledTotalR,
                    wins: scaledWins,
                    losses: scaledLosses
                }
            })

    }, [allPerfData, activeTimeframes, activeTokens, perfPeriod])


    // --- STATS CALCULATION (Reactive) ---
    // Helper to get verified stat for a specific token/tf combination
    const getVerifiedStats = (token: string, timeframe: string) => {
        let sId = "trend_following_native_v1"
        const sName = offering.strategy_name.toLowerCase()
        if (sName.includes("breakout")) sId = "donchian_v2"
        if (sName.includes("reversion")) sId = "mean_reversion_v1"

        const pLabel = perfPeriod === '5y' ? '5Y' : perfPeriod.toUpperCase() // 6m -> 6M
        const key = `${sId}_${token}_${timeframe.toLowerCase()}_${pLabel}` // Ensure lowercase timeframe (1h/4h)

        // @ts-ignore
        return verifiedStats[key]
    }

    // Compute Aggregates from verifiedStats (NOT from filteredData/history which is just placeholder usually)
    // We iterate activeTokens * activeTimeframes
    const allPoints: any[] = []

    // If set is empty, it means "All Selected"
    const tokensToIterate = activeTokens.size > 0 ? Array.from(activeTokens) : uniqueTokens
    const timeframesToIterate = activeTimeframes.size > 0 ? Array.from(activeTimeframes) : uniqueTimeframes

    tokensToIterate.forEach(t => {
        timeframesToIterate.forEach(tf => {
            const stat = getVerifiedStats(t, tf)
            if (stat) allPoints.push({ ...stat, token: t, timeframe: tf })
        })
    })

    const totalTrades = allPoints.reduce((acc, p) => acc + p.total_trades, 0)
    const totalR = allPoints.reduce((acc, p) => acc + p.total_r, 0).toFixed(1)

    const avgWinRate = allPoints.length > 0
        ? (allPoints.reduce((acc, p) => acc + p.win_rate, 0) / allPoints.length).toFixed(1)
        : "0.0"

    const avgRPerTrade = totalTrades > 0 ? Number(totalR) / totalTrades : 0
    const wrDecimal = Number(avgWinRate) / 100
    const estimatedRR = wrDecimal > 0 ? ((avgRPerTrade + (1 - wrDecimal)) / wrDecimal).toFixed(2) : "1.5"


    // --- HELPERS ---
    const toggleToken = (t: string) => {
        const next = new Set(activeTokens)
        if (next.has(t)) {
            next.delete(t)
        } else {
            next.add(t)
        }
        setActiveTokens(next)
    }

    const toggleTimeframe = (tf: string) => {
        const next = new Set(activeTimeframes)
        if (next.has(tf)) next.delete(tf)
        else next.add(tf)
        setActiveTimeframes(next)
    }

    // Colors for tokens (reused logic roughly)
    const getTokenColor = (t: string, isActive: boolean) => {
        if (!isActive) return "text-muted-foreground bg-secondary opacity-50 border-transparent"
        switch (t.toUpperCase()) {
            case 'BTC': return 'text-orange-500 bg-orange-500/10 border-orange-500/20'
            case 'ETH': return 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20'
            case 'SOL': return 'text-teal-400 bg-teal-500/10 border-teal-500/20'
            case 'BNB': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20'
            case 'XRP': return 'text-blue-400 bg-blue-500/10 border-blue-500/20'
            default: return 'text-foreground bg-primary/10 border-primary/20'
        }
    }

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            {/* 80vh height constraint */}
            <DialogContent className="max-w-4xl bg-card border-border shadow-2xl h-[80vh] flex flex-col p-0 gap-0 overflow-hidden outline-none">

                {/* Header */}
                <DialogHeader className="px-6 py-4 border-b border-border/50 shrink-0 bg-background/95 backdrop-blur z-20">
                    <div className="flex items-center gap-3 mb-1.5">
                        <DialogTitle className="text-xl font-bold flex items-center gap-3">
                            {offering.strategy_name}
                            <div className="flex gap-1">
                                {uniqueTimeframes.map(tf => (
                                    <Badge key={tf} variant="outline" className="text-[10px] font-semibold px-1.5 py-0 border-primary/20 bg-primary/5 text-primary">
                                        {tf}
                                    </Badge>
                                ))}
                            </div>
                        </DialogTitle>
                        {!offering.locked && (
                            <Badge variant="secondary" className="gap-1 bg-emerald-500/10 text-emerald-500 border-emerald-500/20 px-2 text-[10px]">
                                <CheckCircle2 className="w-3 h-3" /> Active
                            </Badge>
                        )}
                        {offering.locked && (
                            <Badge variant="secondary" className="gap-1 bg-amber-500/10 text-amber-500 border-amber-500/20 px-2 text-[10px]">
                                <Lock className="w-3 h-3" /> Locked
                            </Badge>
                        )}
                    </div>
                    <DialogDescription className="text-sm text-muted-foreground leading-relaxed max-w-2xl">
                        {details.shortDescription}
                    </DialogDescription>
                </DialogHeader>

                {/* Main Content Area */}
                <Tabs defaultValue="overview" className="flex-1 flex flex-col min-h-0 bg-background/50">
                    <div className="px-6 border-b border-border/40 shrink-0 bg-muted/20">
                        <TabsList className="w-full justify-start h-10 bg-transparent p-0 gap-6">
                            <TabsTrigger value="overview" className="relative h-full rounded-none border-b-2 border-transparent px-0 text-sm font-medium text-muted-foreground data-[state=active]:border-primary data-[state=active]:text-foreground data-[state=active]:shadow-none transition-none focus-visible:ring-0">
                                Overview & Context
                            </TabsTrigger>
                            <TabsTrigger value="performance" className="relative h-full rounded-none border-b-2 border-transparent px-0 text-sm font-medium text-muted-foreground data-[state=active]:border-primary data-[state=active]:text-foreground data-[state=active]:shadow-none transition-none focus-visible:ring-0 group">
                                Performance
                                <Badge className="ml-2 h-4 px-1 text-[9px] bg-primary/10 text-primary group-hover:bg-primary/20 border-primary/20 transition-colors">
                                    Trust Center
                                </Badge>
                            </TabsTrigger>
                        </TabsList>
                    </div>

                    {/* Scrollable Content (Native Scroll for reliability) */}
                    <div className="flex-1 overflow-y-auto w-full relative">
                        <div className="px-6 py-6 pb-12">
                            <TabsContent value="overview" className="mt-0 space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300 outline-none">
                                {/* Key Stats Grid - Compact */}
                                <div className="grid grid-cols-4 gap-3">
                                    <div className="p-3 rounded-lg bg-secondary/10 border border-border/60 flex flex-col items-center text-center">
                                        <TrendingUp className="w-4 h-4 text-emerald-500 mb-1" />
                                        <span className="text-[9px] text-muted-foreground uppercase font-bold tracking-wider">Win Rate</span>
                                        <span className="text-lg font-bold text-foreground mt-0.5 tabular-nums">{avgWinRate}%</span>
                                    </div>
                                    <div className="p-3 rounded-lg bg-secondary/10 border border-border/60 flex flex-col items-center text-center">
                                        <Scale className="w-4 h-4 text-indigo-500 mb-1" />
                                        <span className="text-[9px] text-muted-foreground uppercase font-bold tracking-wider">Avg R:R</span>
                                        <span className="text-lg font-bold text-foreground mt-0.5 tabular-nums">1:{estimatedRR}</span>
                                    </div>
                                    <div className="p-3 rounded-lg bg-secondary/10 border border-border/60 flex flex-col items-center text-center">
                                        <Activity className="w-4 h-4 text-blue-500 mb-1" />
                                        <span className="text-[9px] text-muted-foreground uppercase font-bold tracking-wider">Freq</span>
                                        <span className="text-lg font-bold text-foreground mt-0.5">{details.stats.frequency}</span>
                                    </div>
                                    <div className="p-3 rounded-lg bg-secondary/10 border border-border/60 flex flex-col items-center text-center">
                                        <AlertTriangle className="w-4 h-4 text-amber-500 mb-1" />
                                        <span className="text-[9px] text-muted-foreground uppercase font-bold tracking-wider">Risk</span>
                                        <span className="text-lg font-bold text-foreground mt-0.5">{details.stats.risk}</span>
                                    </div>
                                </div>

                                {/* Educational Context Card */}
                                <div className="rounded-xl border border-border bg-card overflow-hidden shadow-sm">
                                    <div className="bg-secondary/40 px-4 py-2 border-b border-border flex items-center gap-2">
                                        <BookOpen className="w-3.5 h-3.5 text-primary" />
                                        <h3 className="font-semibold text-xs">Market Context</h3>
                                    </div>
                                    <div className="p-4 grid gap-4">
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="space-y-1">
                                                <div className="flex gap-2 items-center">
                                                    <div className="w-1 h-1 rounded-full bg-emerald-500 shrink-0" />
                                                    <h4 className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">When to use</h4>
                                                </div>
                                                <p className="text-sm text-foreground leading-snug pl-3">{details.context.whenToUse}</p>
                                            </div>
                                            <div className="space-y-1">
                                                <div className="flex gap-2 items-center">
                                                    <div className="w-1 h-1 rounded-full bg-red-500 shrink-0" />
                                                    <h4 className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">When to avoid</h4>
                                                </div>
                                                <p className="text-sm text-foreground leading-snug pl-3">{details.context.whenToAvoid}</p>
                                            </div>
                                        </div>
                                        <div className="bg-primary/5 rounded-lg p-3 border border-primary/10 flex gap-3 items-start md:col-span-2">
                                            <Lightbulb className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                                            <div>
                                                <h4 className="text-xs font-bold text-primary">Pro Tip</h4>
                                                <p className="text-xs text-foreground/80 mt-1 italic leading-relaxed">"{details.context.proTip}"</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-2 pb-4">
                                    <h3 className="text-sm font-semibold flex items-center gap-2 text-foreground/90">
                                        <BarChart3 className="w-4 h-4 text-muted-foreground" />
                                        Technical Logic
                                    </h3>
                                    <div className="pl-1">
                                        <p className="text-sm text-muted-foreground leading-relaxed mb-3">{details.longDescription}</p>
                                        <ul className="grid sm:grid-cols-2 gap-x-4 gap-y-2">
                                            {details.features.map((feature, i) => (
                                                <li key={i} className="flex items-center gap-2 text-foreground/80 text-xs">
                                                    <div className="w-1 h-1 rounded-full bg-primary shrink-0" />
                                                    {feature}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            </TabsContent>

                            <TabsContent value="performance" className="mt-0 space-y-6 animate-in fade-in slide-in-from-right-4 duration-300 outline-none">
                                {/* Filters Toolbar */}
                                <div className="flex flex-col gap-3">
                                    <div className="flex items-center justify-between gap-4 flex-wrap">
                                        {/* Token Multi-select */}
                                        <div className="flex items-center gap-1.5 flex-wrap">
                                            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide mr-1">Assets:</span>
                                            {uniqueTokens.map(t => {
                                                const isActive = activeTokens.size === 0 || activeTokens.has(t)
                                                return (
                                                    <button
                                                        key={t}
                                                        onClick={() => toggleToken(t)}
                                                        className={cn(
                                                            "px-2 py-0.5 rounded text-[10px] font-bold border transition-all",
                                                            getTokenColor(t, isActive)
                                                        )}
                                                    >
                                                        {t}
                                                    </button>
                                                )
                                            })}
                                        </div>

                                        {/* Period Selector */}
                                        <div className="flex bg-secondary/50 p-0.5 rounded-lg border border-border/50">
                                            {(["6m", "2y", "5y"] as const).map((p) => (
                                                <button
                                                    key={p}
                                                    onClick={() => setPerfPeriod(p)}
                                                    className={cn(
                                                        "px-3 py-1 text-[10px] font-bold rounded-md transition-all",
                                                        perfPeriod === p
                                                            ? "bg-background text-foreground shadow-sm border border-black/5 dark:border-white/5"
                                                            : "text-muted-foreground hover:text-foreground hover:bg-black/5 dark:hover:bg-white/5"
                                                    )}
                                                >
                                                    {p === "5y" ? "5Y (Max)" : p.toUpperCase()}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Timeframe Multi-select */}
                                    <div className="flex items-center gap-1.5 flex-wrap">
                                        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide mr-1">Timeframe:</span>
                                        {uniqueTimeframes.map(tf => {
                                            const isActive = activeTimeframes.size === 0 || activeTimeframes.has(tf)
                                            return (
                                                <button
                                                    key={tf}
                                                    onClick={() => toggleTimeframe(tf)}
                                                    className={cn(
                                                        "px-2.5 py-0.5 rounded text-[10px] font-bold border transition-all",
                                                        isActive
                                                            ? "bg-primary text-primary-foreground border-primary shadow-sm"
                                                            : "bg-secondary/40 text-muted-foreground border-transparent hover:bg-secondary/60"
                                                    )}
                                                >
                                                    {tf}
                                                </button>
                                            )
                                        })}
                                    </div>
                                </div>



                                {/* Aggregated Stats Card */}
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    <div className="bg-card border border-border rounded-xl p-5 relative overflow-hidden group">
                                        <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                                            <TrendingUp className="w-16 h-16 text-emerald-500" />
                                        </div>
                                        <div className="relative z-10">
                                            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-1">Real Win Rate</p>
                                            <div className="flex items-baseline gap-2">
                                                <h3 className="text-3xl font-bold text-white tabular-nums tracking-tight">{avgWinRate}%</h3>
                                            </div>
                                            <div className="flex items-center gap-1.5 mt-2">
                                                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                                <span className="text-[10px] font-medium text-muted-foreground">Avg Selected Assets</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="bg-card border border-border rounded-xl p-5 relative overflow-hidden group">
                                        <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                                            <BadgeDollarSign className="w-16 h-16 text-emerald-400" />
                                        </div>
                                        <div className="relative z-10">
                                            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-1">Total Profit (R)</p>
                                            <div className="flex items-baseline gap-2">
                                                <h3 className={cn(
                                                    "text-2xl font-bold tabular-nums tracking-tight",
                                                    Number(totalR) >= 0 ? "text-emerald-400" : "text-rose-400"
                                                )}>
                                                    {Number(totalR) > 0 ? "+" : ""}{totalR}R
                                                </h3>
                                            </div>
                                            <p className="text-[10px] text-muted-foreground mt-2 font-medium">Net Profit ({perfPeriod === '5y' ? '5y' : perfPeriod.toUpperCase()})</p>
                                        </div>
                                    </div>

                                    <div className="bg-card border border-border rounded-xl p-5 relative overflow-hidden group">
                                        <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                                            <Activity className="w-16 h-16 text-blue-500" />
                                        </div>
                                        <div className="relative z-10">
                                            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-1">Total Trades</p>
                                            <h3 className="text-3xl font-bold text-white tabular-nums tracking-tight">{totalTrades}</h3>
                                            <div className="inline-flex items-center mt-2 px-2 py-0.5 rounded text-[9px] font-bold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                                                VERIFIED {perfPeriod === '5y' ? '5Y' : perfPeriod.toUpperCase()}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Detailed Table */}
                                <div className="rounded-xl border border-border overflow-hidden bg-card/50">
                                    <Table>
                                        <TableHeader className="bg-secondary/40">
                                            <TableRow className="hover:bg-transparent border-border/50">
                                                <TableHead className="w-[100px] text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Asset</TableHead>
                                                <TableHead className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Timeframe</TableHead>
                                                <TableHead className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Win Rate</TableHead>
                                                <TableHead className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Total R</TableHead>
                                                <TableHead className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Trades</TableHead>
                                                <TableHead className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground text-right pr-6">W / L</TableHead>
                                                <TableHead className="w-[60px] text-center"></TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {allPoints.map((stat, idx) => (
                                                <TableRow key={idx} className="border-border/40 hover:bg-secondary/20 transition-colors group">
                                                    <TableCell className="font-bold text-xs">{stat.token}</TableCell>
                                                    <TableCell className="text-xs text-muted-foreground font-mono">{stat.timeframe}</TableCell>
                                                    <TableCell className="font-mono text-xs font-medium">{stat.win_rate}%</TableCell>
                                                    <TableCell className={cn(
                                                        "font-mono text-xs font-bold",
                                                        stat.total_r >= 0 ? "text-emerald-400" : "text-rose-400"
                                                    )}>
                                                        {stat.total_r > 0 ? "+" : ""}{stat.total_r}R
                                                    </TableCell>
                                                    <TableCell className="text-xs text-muted-foreground">{stat.total_trades}</TableCell>
                                                    <TableCell className="text-xs font-mono text-right pr-6">
                                                        <span className="text-emerald-500">{stat.wins}</span>
                                                        <span className="text-muted-foreground mx-1">/</span>
                                                        <span className="text-rose-500">{stat.losses}</span>
                                                    </TableCell>
                                                    <TableCell className="text-center">
                                                        <Button
                                                            variant="ghost"
                                                            size="icon"
                                                            className="h-8 w-8 opacity-70 group-hover:opacity-100 transition-all hover:bg-secondary hover:text-primary"
                                                            onClick={() => handleDownloadLedger(stat, offering.strategy_name, perfPeriod)}
                                                            title="Download Verified Ledger"
                                                        >
                                                            <Download className="w-4 h-4" />
                                                        </Button>
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </div>
                            </TabsContent>
                        </div>
                    </div >

                    {/* Footer - Only Upgrade CTA if needed */}
                    {
                        offering.locked && offering.locked_reason === 'UPGRADE_REQUIRED' && (
                            <DialogFooter className="px-6 py-3 border-t border-border shrink-0 bg-background/95 backdrop-blur z-20">
                                <Button size="sm" className="w-full sm:w-auto bg-primary text-primary-foreground hover:bg-primary/90 min-w-[200px]" onClick={() => window.location.href = '/pricing'}>
                                    Upgrade to SwingPro
                                </Button>
                            </DialogFooter>
                        )
                    }
                </Tabs >
            </DialogContent >
        </Dialog >
    )
}

// --- DOWNLOAD HELPER ---
import realLedger from '@/data/real_ledger.json'

// --- DOWNLOAD HELPER ---
import { BASE_URL } from '@/lib/api-client'

function handleDownloadLedger(row: PerformanceMetric, strategyName: string, period: string) {
    // Construct the backend URL
    const params = new URLSearchParams({
        strategy_name: strategyName,
        period: period,
        token: row.token,
        timeframe: row.timeframe
    })

    // Use the same BASE_URL as the rest of the app
    const downloadUrl = `${BASE_URL}/api/strategies/download_ledger?${params.toString()}`

    // Trigger download
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = `Ledger_${strategyName.replace(/\s+/g, '_')}_${row.token}_${period.toUpperCase()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
}

// --- MOCK DATA ---
function getStrategyDetails(code: string) {
    if (code === 'donchian' || code === 'donchian_v2' || code === 'TITAN_BREAKOUT') {
        return {
            shortDescription: "High-volatility breakout system designed to capture explosive moves.",
            longDescription: "Titan Breakout monitors Volatility Contractions. When price pierces the 20-period Donchian Channel with momentum (confirmed by Volume & RSI), it triggers an entry, aiming to catch the 'Fat tails' of crypto distributions.",
            stats: { winRate: "39%", frequency: "High", risk: "Mod-High" },
            context: {
                whenToUse: "Strong directional trends, Bull Markets.",
                whenToAvoid: "Choppy sideways ranges.",
                proTip: "SOL and Meme coins tend to respect breakouts more than BTC due to retail fomo."
            },
            features: [
                "20-period Donchian Breakout",
                "RSI Cool-off Filter",
                "Trailing Stop (ATR)",
                "High R:R Ratio"
            ],
            idealFor: ""
        }
    }
    if (code === 'trend_following_native_v1' || code === 'TREND_FOLLOWING' || code === 'FLOW_MASTER') {
        return {
            shortDescription: "Conservative trend-following engine surfing institutional flows.",
            longDescription: "Flow Master waits for the trend to be established (Price > EMA200) and confirms strength with ADX > 20. It filters out low-quality noise to protect capital.",
            stats: { winRate: "48%", frequency: "Medium", risk: "Low" },
            context: {
                whenToUse: "Sustained trends (e.g. BTC above 200 DMA).",
                whenToAvoid: "High volatility chop.",
                proTip: "Use 4H timeframe for much cleaner signals and higher Win Rate."
            },
            features: [
                "EMA 200 Trend Filter",
                "ADX > 20 Confirmation",
                "Volume Validation",
                "Low Drawdown"
            ],
            idealFor: ""
        }
    }
    if (code === 'mean_reversion_v1' || code === 'MEAN_REVERSION') {
        return {
            shortDescription: "Fades market extremes to capture rapid snap-backs.",
            longDescription: "Markets range 70% of the time. This strategy buys when price falls below the Lower Bollinger Band (2.5 std) and RSI is oversold (<30).",
            stats: { winRate: "64%", frequency: "Low", risk: "Moderate" },
            context: {
                whenToUse: "Ranging/Crab markets.",
                whenToAvoid: "Strong parabolic trends.",
                proTip: "If a candle closes OUTSIDE the band, the reversion signal is stronger."
            },
            features: [
                "Bollinger Bands (2.5)",
                "RSI Divergence",
                "SMA 20 Target",
                "High Probability"
            ],
            idealFor: ""
        }
    }

    return {
        shortDescription: "Advanced algorithmic trading system.",
        longDescription: "Uses statistical analysis to find edge cases in the market.",
        stats: { winRate: "--", frequency: "--", risk: "--" },
        context: { whenToUse: "--", whenToAvoid: "--", proTip: "--" },
        features: ["Algorithmic execution", "Risk management"],
        idealFor: ""
    }
}
