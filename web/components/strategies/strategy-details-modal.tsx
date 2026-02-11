"use client"

import { useState, useMemo, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { CheckCircle2, TrendingUp, Activity, BarChart3, AlertTriangle, Lock, BookOpen, Ban, Lightbulb, Scale, Filter, Download, BadgeDollarSign, X, BrainCircuit, Zap, Construction, Target, Clock, ShieldCheck, ArrowUpRight } from "lucide-react"
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
    const [activeTokens, setActiveTokens] = useState<Set<string>>(new Set())
    const [activeTimeframes, setActiveTimeframes] = useState<Set<string>>(new Set())

    useEffect(() => {
        if (open && offering) {
            if (variants && variants.length > 0) setActiveTimeframes(new Set(variants.map(v => v.timeframe)))
            else setActiveTimeframes(new Set([offering.timeframe]))
            setActiveTokens(new Set())
        }
    }, [open, offering, variants])

    const theme = useMemo(() => {
        if (!offering) return { accent: "text-muted-foreground", border: "border-border", bg: "bg-muted/50", bar: "bg-muted-foreground" }
        const code = offering.strategy_code
        if (code === 'DONCHIAN_V2') return { accent: "text-orange-500", border: "border-orange-500/20", bg: "bg-orange-500/10", bar: "bg-orange-500", grad: "from-orange-500/5 via-transparent" }
        if (code === 'SUPER_TREND') return { accent: "text-emerald-500", border: "border-emerald-500/20", bg: "bg-emerald-500/10", bar: "bg-emerald-500", grad: "from-emerald-500/5 via-transparent" }
        if (code.includes('REVERSION')) return { accent: "text-indigo-500", border: "border-indigo-500/20", bg: "bg-indigo-500/10", bar: "bg-indigo-500", grad: "from-indigo-500/5 via-transparent" }
        return { accent: "text-cyan-500", border: "border-cyan-500/20", bg: "bg-cyan-500/10", bar: "bg-cyan-500", grad: "from-cyan-500/5 via-transparent" }
    }, [offering])

    if (!offering) return null

    const details = getStrategyDetails(offering.strategy_code)

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            {/* Using semantic colors for Light/Dark mode compatibility */}
            <DialogContent className={cn(
                "max-w-3xl bg-background/95 backdrop-blur-xl border-border shadow-2xl p-0 gap-0 outline-none flex flex-col h-[85vh] sm:h-[650px] overflow-hidden",
                theme.border
            )}>

                {/* Header with subtle gradient */}
                <div className={cn("relative px-6 py-5 border-b border-border/60 shrink-0 bg-card/40 flex items-start justify-between overflow-hidden")}>
                    {/* Background Gradient for Header */}
                    <div className={cn("absolute inset-0 bg-gradient-to-br opacity-30 pointer-events-none", theme.grad)} />

                    <div className="space-y-1.5 relative z-10">
                        <div className="flex items-center gap-3">
                            <DialogTitle className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2.5">
                                {offering.strategy_name}
                            </DialogTitle>
                            {!offering.locked ? (
                                <Badge variant="outline" className={cn("gap-1.5 px-2.5 py-0.5 text-[10px] uppercase font-bold tracking-wider bg-background/50 backdrop-blur-sm", theme.border, theme.accent)}>
                                    <div className={cn("w-1.5 h-1.5 rounded-full animate-pulse", theme.bar)} /> ONLINE
                                </Badge>
                            ) : (
                                <Badge variant="outline" className="gap-1.5 px-2.5 py-0.5 text-[10px] uppercase font-bold tracking-wider bg-amber-500/10 text-amber-600 border-amber-500/20">
                                    <Lock className="w-3 h-3" /> PRO
                                </Badge>
                            )}
                        </div>
                        <DialogDescription className="text-xs font-medium text-muted-foreground/80 max-w-lg line-clamp-1">
                            {details.shortDescription}
                        </DialogDescription>
                    </div>
                </div>

                <Tabs defaultValue="overview" className="flex-1 flex flex-col min-h-0 bg-background/30">
                    {/* Tabs List */}
                    <div className="px-6 border-b border-border/40 shrink-0 bg-muted/20 backdrop-blur-sm sticky top-0 z-20">
                        <TabsList className="bg-transparent p-0 gap-8 h-11 w-full justify-start">
                            <TabsTrigger value="overview" className="h-full rounded-none border-b-2 border-transparent px-0 text-xs font-bold uppercase tracking-wider text-muted-foreground/70 data-[state=active]:text-foreground data-[state=active]:border-primary transition-all hover:text-foreground/90">
                                Profile & Edge
                            </TabsTrigger>
                            <TabsTrigger value="specs" className="h-full rounded-none border-b-2 border-transparent px-0 text-xs font-bold uppercase tracking-wider text-muted-foreground/70 data-[state=active]:text-foreground data-[state=active]:border-primary transition-all hover:text-foreground/90">
                                Technical Specs
                            </TabsTrigger>
                            <TabsTrigger value="performance" className="h-full rounded-none border-b-2 border-transparent px-0 text-xs font-bold uppercase tracking-wider text-muted-foreground/70 data-[state=active]:text-foreground data-[state=active]:border-primary transition-all hover:text-foreground/90 group flex items-center gap-2">
                                Verified Data
                            </TabsTrigger>
                        </TabsList>
                    </div>

                    <ScrollArea className="flex-1">
                        <div className="p-6 h-full space-y-8">

                            {/* TAB 1: PROFILE */}
                            <TabsContent value="overview" className="mt-0 space-y-6 outline-none animate-in fade-in slide-in-from-bottom-2 duration-300">
                                {/* Hero Stats Grid - Enhanced visibility */}
                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                                    <StatBox
                                        icon={<Target className="w-4 h-4" />}
                                        label="Win Rate"
                                        value={details.expectations.winRate}
                                        sub="Expected"
                                        accent={theme.accent}
                                        bg={theme.bg}
                                    />
                                    <StatBox
                                        icon={<Scale className="w-4 h-4" />}
                                        label="Risk : Reward"
                                        value={details.expectations.riskReward}
                                        sub="Target Ratio"
                                    />
                                    <StatBox
                                        icon={<Clock className="w-4 h-4" />}
                                        label="Frequency"
                                        value={details.expectations.frequency}
                                        sub="Activity Signal"
                                    />
                                    <StatBox
                                        icon={<ShieldCheck className="w-4 h-4" />}
                                        label="Risk Profile"
                                        value={details.expectations.risk}
                                        sub="Drawdown Est."
                                    />
                                </div>

                                {/* Main Description Card */}
                                <div className="rounded-xl border border-border/60 bg-card p-6 shadow-sm relative overflow-hidden group">
                                    <div className={cn("absolute inset-0 opacity-5 bg-gradient-to-br transition-opacity group-hover:opacity-10", theme.grad)} />
                                    <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-3 flex items-center gap-2 relative z-10">
                                        <BrainCircuit className="w-4 h-4 text-foreground/70" /> Core Philosophy
                                    </h3>
                                    <p className="text-sm text-foreground/90 leading-relaxed font-medium relative z-10">
                                        {details.longDescription}
                                    </p>
                                </div>

                                {/* Market Context - Two Columns */}
                                <div className="grid sm:grid-cols-2 gap-4">
                                    <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-5 relative overflow-hidden">
                                        <div className="absolute top-0 right-0 p-3 opacity-10">
                                            <TrendingUp className="w-12 h-12 text-emerald-500" />
                                        </div>
                                        <div className="flex items-center gap-2 mb-3 relative z-10">
                                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                                            <h3 className="text-[10px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">Best Conditions</h3>
                                        </div>
                                        <p className="text-xs font-medium text-foreground/80 leading-relaxed relative z-10">
                                            {details.context.bestPeriod}
                                        </p>
                                    </div>

                                    <div className="rounded-xl border border-rose-500/20 bg-rose-500/5 p-5 relative overflow-hidden">
                                        <div className="absolute top-0 right-0 p-3 opacity-10">
                                            <AlertTriangle className="w-12 h-12 text-rose-500" />
                                        </div>
                                        <div className="flex items-center gap-2 mb-3 relative z-10">
                                            <div className="w-1.5 h-1.5 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]" />
                                            <h3 className="text-[10px] font-bold uppercase tracking-wider text-rose-600 dark:text-rose-400">Drawdown Risk</h3>
                                        </div>
                                        <p className="text-xs font-medium text-foreground/80 leading-relaxed relative z-10">
                                            {details.context.worstPeriod}
                                        </p>
                                    </div>
                                </div>
                            </TabsContent>

                            {/* TAB 2: SPECS */}
                            <TabsContent value="specs" className="mt-0 space-y-6 outline-none animate-in fade-in slide-in-from-right-2 duration-300">
                                <div className="grid md:grid-cols-3 gap-6 h-full">
                                    {/* Parameters Column */}
                                    <div className="md:col-span-1 space-y-4">
                                        <div className="rounded-xl border border-border/60 bg-card p-5 h-full shadow-sm">
                                            <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-4 flex items-center gap-2">
                                                <Filter className="w-3.5 h-3.5" /> Parameters
                                            </h3>
                                            <div className="space-y-3">
                                                {details.technical.parameters.map((param, i) => (
                                                    <div key={i} className="flex flex-col border-b border-border/40 pb-2 last:border-0 last:pb-0">
                                                        <span className="text-[10px] font-bold text-muted-foreground uppercase mb-0.5">{param.name}</span>
                                                        <span className="text-sm font-mono font-semibold text-foreground">{param.value}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Mechanics Column */}
                                    <div className="md:col-span-2 space-y-4 flex flex-col">
                                        <div className="rounded-xl border border-border/60 bg-card p-5 shadow-sm">
                                            <h3 className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-3 flex items-center gap-2">
                                                <Zap className="w-3.5 h-3.5" /> Mechanics Logic
                                            </h3>
                                            <p className="text-sm text-foreground/80 leading-relaxed font-mono bg-muted/30 p-4 rounded-lg border border-border/40">
                                                {details.technical.mechanics}
                                            </p>
                                        </div>

                                        {/* Indicators Tags */}
                                        <div className="flex flex-wrap gap-2">
                                            {details.features.map((f, i) => (
                                                <Badge key={i} variant="secondary" className="bg-secondary/50 hover:bg-secondary/70 text-xs font-mono border-border/40 px-3 py-1 text-muted-foreground">
                                                    {f}
                                                </Badge>
                                            ))}
                                        </div>

                                        {/* Pine Script Placeholder */}
                                        <div className="flex-1 min-h-[140px] border border-dashed border-border/60 rounded-xl p-6 flex flex-col items-center justify-center text-center bg-muted/10">
                                            <div className="w-10 h-10 rounded-full bg-muted/20 flex items-center justify-center mb-3">
                                                <code className="text-xs font-bold text-muted-foreground">{'</>'}</code>
                                            </div>
                                            <h4 className="text-sm font-bold text-foreground">Pine Script Source</h4>
                                            <p className="text-xs text-muted-foreground mt-1.5 max-w-[240px]">
                                                Copy-paste compatible scripts for TradingView backtesting arriving in <span className="font-bold text-foreground">v2.1</span>
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </TabsContent>

                            {/* TAB 3: DATA (COMING SOON) */}
                            <TabsContent value="performance" className="mt-0 h-full flex flex-col items-center justify-center outline-none animate-in fade-in slide-in-from-right-2 duration-300 min-h-[400px]">
                                <div className="flex flex-col items-center justify-center text-center space-y-6 max-w-md mx-auto p-8 rounded-2xl bg-gradient-to-b from-transparent to-muted/10 border border-transparent">
                                    <div className="w-20 h-20 rounded-3xl bg-card border border-border/60 flex items-center justify-center shadow-xl relative overflow-hidden group">
                                        <div className={cn("absolute inset-0 opacity-10 bg-gradient-to-br group-hover:opacity-20 transition-all", theme.grad)} />
                                        <Activity className="w-10 h-10 text-muted-foreground group-hover:text-foreground transition-colors" />
                                    </div>
                                    <div className="space-y-2">
                                        <h3 className="text-xl font-bold text-foreground tracking-tight">Verified Performance Audit</h3>
                                        <p className="text-sm text-muted-foreground leading-relaxed">
                                            We are currently processing the historical ledger for this strategy to ensure 100% accuracy. Verified PnL data will be available shortly.
                                        </p>
                                    </div>
                                    <Badge variant="outline" className="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20 text-[10px] py-1 px-3 tracking-wide uppercase font-bold shadow-sm">
                                        <Construction className="w-3 h-3 mr-1.5" /> Audit In Progress
                                    </Badge>
                                </div>
                            </TabsContent>
                        </div>
                    </ScrollArea>
                </Tabs>
            </DialogContent>
        </Dialog>
    )
}

function StatBox({ icon, label, value, sub, accent, bg }: { icon?: React.ReactNode, label: string, value: string, sub: string, accent?: string, bg?: string }) {
    return (
        <div className={cn("p-4 rounded-xl border border-border/50 flex flex-col items-start justify-between min-h-[100px] shadow-sm transition-all hover:shadow-md hover:border-border/80 bg-card group", bg)}>
            <div className="flex items-center justify-between w-full mb-2">
                <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">{label}</span>
                {icon && <div className="text-muted-foreground/40 group-hover:text-foreground/60 transition-colors">{icon}</div>}
            </div>
            <div>
                <span className={cn("text-xl font-mono font-bold tracking-tight block", accent || "text-foreground")}>{value}</span>
                <span className="text-[10px] text-muted-foreground/70 font-medium">{sub}</span>
            </div>
        </div>
    )
}

// ... EXISTING HELPERS ...
function getStrategyDetails(code: string) {
    if (code === 'donchian' || code === 'donchian_v2' || code === 'TITAN_BREAKOUT') {
        return {
            shortDescription: "Adaptive volatility breakout system.",
            longDescription: "Titan Breakout operates in 'Scientific Mode', differentiating between intraday scalps and swing trends. It sacrifices win rate for high R:R ratios using a 20/10 split-window logic.",
            expectations: { winRate: "39-45%", riskReward: "1:3.5", frequency: "High", risk: "Mod-High" },
            context: { bestPeriod: "Strong directional trends (Bull/Bear Runs).", worstPeriod: "Choppy sideways ranges." },
            features: ["Split-Window", "RSI Filter", "ATR Trail"],
            technical: {
                mechanics: "Monitors a 20-period High/Low channel. Break above high + RSI check triggers Long. Exit trails price using 2.5x ATR band.",
                parameters: [{ name: "Channel", value: "20/10" }, { name: "ATR Mult", value: "2.5x" }, { name: "Filter", value: "RSI < 70" }]
            }
        }
    }
    if (code === 'supertrend_v1' || code === 'SUPER_TREND') {
        return {
            shortDescription: "Pure volatility-based trend following.",
            longDescription: "SuperTrend captures trend 'meat' using ATR. Flips bullish when price closes above the volatility band. The ultimate anti-noise tool for sustained moves.",
            expectations: { winRate: "45-50%", riskReward: "1:2.0", frequency: "High", risk: "Medium" },
            context: { bestPeriod: "Explosive volatility & clear trends.", worstPeriod: "Low vol consolidation." },
            features: ["ATR Trail", "Vol Adjust", "No Lag"],
            technical: {
                mechanics: "Calculates ATR band. Close > Band = Green (Long). Band trails price but never moves against it.",
                parameters: [{ name: "ATR Len", value: "10" }, { name: "Factor", value: "3.0" }, { name: "Source", value: "Close" }]
            }
        }
    }
    if (code === 'mean_reversion_v1' || code === 'MEAN_REVERSION') {
        return {
            shortDescription: "Fades market extremes for snap-backs.",
            longDescription: "Markets range 70% of time. Shorts tops and buys bottoms when price deviates significantly (StdDev) from mean, targeting equilibrium.",
            expectations: { winRate: "65-72%", riskReward: "1:1.2", frequency: "Low", risk: "Moderate" },
            context: { bestPeriod: "Ranging/Crab markets.", worstPeriod: "Strong parabolic trends." },
            features: ["Bollinger", "RSI Div", "SMA Mean"],
            technical: {
                mechanics: "Long if Price < Lower BB AND RSI < 30. Exit on Mean touch or RSI > 50.",
                parameters: [{ name: "BB Len", value: "20" }, { name: "StdDev", value: "2.5" }, { name: "RSI", value: "< 30" }]
            }
        }
    }
    return {
        shortDescription: "Scientific SMA Crossover engine.",
        longDescription: "Optimized Golden Cross filtered by ADX. Dynamic exit using Death Cross or tight trail. Designed for sustained directional moves.",
        expectations: { winRate: "42-48%", riskReward: "1:2.5", frequency: "Medium", risk: "Low" },
        context: { bestPeriod: "Sustained trends (BTC > 200DMA).", worstPeriod: "Whipsaw / Flat ADX." },
        features: ["SMA Cross", "ADX Filter", "Dyn Risk"],
        technical: {
            mechanics: "Buy: Fast SMA(20) > Slow SMA(50) AND ADX > 25. Filters fake-outs common in basic crosses.",
            parameters: [{ name: "Fast", value: "20" }, { name: "Slow", value: "50" }, { name: "ADX", value: "> 25" }]
        }
    }
}
