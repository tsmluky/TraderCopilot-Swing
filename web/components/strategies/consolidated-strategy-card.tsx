"use client"

import { useState, useMemo } from "react"
import { TrendingUp, Lock, ArrowUpRight, Clock, Zap, Activity, Waves, RotateCcw } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"
import Link from "next/link"
import { StrategyDetailsModal } from "./strategy-details-modal"

// Reusing the interface from master-strategy-card
export interface StrategyOffering {
    id: string
    strategy_code: string
    strategy_name: string
    timeframe: string
    tokens: string[]
    all_tokens?: string[]
    locked: boolean
    locked_reason?: string
    plan_required?: string
    badges?: string[]
    win_rate?: string
    total_signals?: number
}

interface ConsolidatedStrategyCardProps {
    strategyName: string
    strategyCode: string
    description: string
    variants: StrategyOffering[] // List of offerings for this strategy (e.g. 1H, 4H, 1D)
}

export function ConsolidatedStrategyCard({ strategyName, strategyCode, description, variants }: ConsolidatedStrategyCardProps) {
    // Sort variants by timeframe logic (1H -> 4H) and exclude 1D
    const sortedVariants = useMemo(() => {
        const order = ["1H", "4H", "1D", "1W"]
        // Filter out 1D as per user request (not enough signals)
        return [...variants]
            .filter(v => v.timeframe !== '1D')
            .sort((a, b) => {
                return order.indexOf(a.timeframe) - order.indexOf(b.timeframe)
            })
    }, [variants])

    // Default to the first available (unlocked) variant, or just the first one
    const defaultVariant = sortedVariants.find(v => !v.locked) || sortedVariants[0]
    const [selectedVariant, setSelectedVariant] = useState<StrategyOffering>(defaultVariant)
    const [showDetails, setShowDetails] = useState(false)

    // THEME LOGIC
    const theme = useMemo(() => {
        if (strategyCode === 'TITAN_BREAKOUT') {
            return {
                accent: "text-orange-500",
                bgGradient: "from-orange-500/10 to-purple-500/5",
                buttonActive: "bg-orange-500 hover:bg-orange-600",
                icon: <Zap className="w-5 h-5 text-orange-500" />,
                borderHover: "group-hover:border-orange-500/30",
                glow: "from-orange-500/20 to-purple-600/20",
                chartColor: "#f97316" // orange-500
            }
        } else if (strategyCode === 'MEAN_REVERSION' || strategyCode === 'mean_reversion_v1') {
            return {
                accent: "text-fuchsia-500",
                bgGradient: "from-fuchsia-500/10 to-pink-500/5",
                buttonActive: "bg-fuchsia-500 hover:bg-fuchsia-600",
                icon: <RotateCcw className="w-5 h-5 text-fuchsia-500" />,
                borderHover: "group-hover:border-fuchsia-500/30",
                glow: "from-fuchsia-500/20 to-pink-600/20",
                chartColor: "#d946ef" // fuchsia-500
            }
        } else {
            return {
                accent: "text-cyan-500",
                bgGradient: "from-cyan-500/10 to-blue-500/5",
                buttonActive: "bg-cyan-500 hover:bg-cyan-600",
                icon: <Waves className="w-5 h-5 text-cyan-500" />,
                borderHover: "group-hover:border-cyan-500/30",
                glow: "from-cyan-500/20 to-blue-600/20",
                chartColor: "#06b6d4" // cyan-500
            }
        }
    }, [strategyCode])

    // Token Colors Helper
    const getTokenColor = (t: string) => {
        switch (t.toUpperCase()) {
            case 'BTC': return 'text-orange-500 bg-orange-500/10 border-orange-500/20'
            case 'ETH': return 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20'
            case 'SOL': return 'text-teal-400 bg-teal-500/10 border-teal-500/20'
            case 'BNB': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20'
            case 'XRP': return 'text-blue-400 bg-blue-500/10 border-blue-500/20'
            default: return 'text-muted-foreground bg-secondary'
        }
    }

    if (!selectedVariant) return null

    const isLocked = selectedVariant.locked

    return (
        <>
            <div className="relative group h-full">
                {/* Background Glow Effect */}
                <div className={cn(
                    "absolute -inset-0.5 bg-gradient-to-r rounded-3xl blur-xl opacity-20 group-hover:opacity-60 transition duration-700 pointer-events-none mix-blend-multiply dark:mix-blend-normal",
                    theme.glow
                )} />

                <Card className={cn(
                    "relative h-full min-h-[340px] bg-white dark:bg-card/40 backdrop-blur-xl border-black/5 dark:border-white/5 overflow-hidden transition-all duration-300 flex flex-col shadow-sm dark:shadow-none hover:shadow-xl dark:hover:shadow-none",
                    theme.borderHover
                )}>
                    {/* Interior Background Decoration */}
                    <div className={cn("absolute inset-0 bg-gradient-to-br opacity-30 dark:opacity-50 transition-opacity", theme.bgGradient)} />
                    <div className="absolute inset-0 bg-grid-black/5 dark:bg-grid-white/5 mask-image-linear-gradient-to-b opacity-50 dark:opacity-30" />

                    {/* Header */}
                    <CardHeader className="relative pb-2 pt-5 px-5 z-10">
                        <div className="flex flex-col md:flex-row md:items-start justify-between gap-3">
                            <div className="flex gap-3">
                                <div className={cn("h-10 w-10 rounded-xl bg-white dark:bg-background/50 border border-black/5 dark:border-white/10 flex items-center justify-center shadow-md dark:shadow-inner mt-0.5 shrink-0")}>
                                    {theme.icon}
                                </div>
                                <div className="space-y-0.5">
                                    <CardTitle className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
                                        {strategyName}
                                    </CardTitle>
                                    <CardDescription className="text-xs font-medium text-muted-foreground/80 leading-snug">
                                        {description}
                                    </CardDescription>
                                </div>
                            </div>
                        </div>
                    </CardHeader>

                    {/* Content */}
                    <CardContent className="relative flex-1 z-10 pt-2 px-5 pb-5 flex flex-col justify-between gap-4">

                        {/* Metrics Grid */}
                        <div className="grid grid-cols-3 gap-2">
                            {/* Win Rate */}
                            <div className="space-y-0.5 p-2.5 rounded-xl bg-black/5 dark:bg-black/20 border border-black/5 dark:border-white/5 relative overflow-hidden group/metric">
                                <div className="absolute inset-0 bg-gradient-to-br from-white/40 dark:from-white/5 to-transparent opacity-0 group-hover/metric:opacity-100 transition-opacity" />
                                <div className="flex items-center gap-1.5 text-[9px] font-bold text-muted-foreground uppercase tracking-wider z-10 relative">
                                    <TrendingUp className="w-3 h-3" /> Win Rate
                                </div>
                                <div className={cn("text-lg font-black tabular-nums mt-0.5 z-10 relative", isLocked ? "text-muted-foreground blur-[3px]" : "text-foreground")}>
                                    {selectedVariant.win_rate || "N/A"}
                                </div>
                                {/* Visual decor line */}
                                <div className={cn("absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r opacity-50", theme.bgGradient)} />
                            </div>

                            {/* Signals */}
                            <div className="space-y-0.5 p-2.5 rounded-xl bg-black/5 dark:bg-black/20 border border-black/5 dark:border-white/5 relative overflow-hidden group/metric">
                                <div className="absolute inset-0 bg-gradient-to-br from-white/40 dark:from-white/5 to-transparent opacity-0 group-hover/metric:opacity-100 transition-opacity" />
                                <div className="flex items-center gap-1.5 text-[9px] font-bold text-muted-foreground uppercase tracking-wider z-10 relative">
                                    <Activity className="w-3 h-3" /> Signals
                                </div>
                                <div className={cn("text-lg font-black tabular-nums mt-0.5 z-10 relative", isLocked ? "text-muted-foreground blur-[3px]" : "text-foreground")}>
                                    {selectedVariant.total_signals || 0}
                                </div>
                            </div>

                            {/* Frequency */}
                            <div className="space-y-0.5 p-2.5 rounded-xl bg-black/5 dark:bg-black/20 border border-black/5 dark:border-white/5 relative overflow-hidden group/metric">
                                <div className="absolute inset-0 bg-gradient-to-br from-white/40 dark:from-white/5 to-transparent opacity-0 group-hover/metric:opacity-100 transition-opacity" />
                                <div className="flex items-center gap-1.5 text-[9px] font-bold text-muted-foreground uppercase tracking-wider z-10 relative">
                                    <Clock className="w-3 h-3" /> Pace
                                </div>
                                <div className="text-base font-bold text-foreground mt-1 z-10 relative truncate">
                                    {selectedVariant.timeframe === '1H' ? 'Intraday' : selectedVariant.timeframe === '4H' ? 'Swing' : 'Long Term'}
                                </div>
                            </div>
                        </div>

                        {/* Tokens & CTA */}
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <div className="text-[9px] font-bold text-muted-foreground/60 uppercase tracking-widest pl-1">
                                    Active Markets
                                </div>
                            </div>

                            <div className="flex flex-wrap gap-1.5 min-h-[28px]">
                                {/* If locked, show only locked tokens view or blurred view */}
                                {selectedVariant.all_tokens?.map((token) => {
                                    const isIncluded = selectedVariant.tokens.includes(token)
                                    const tokenLocked = isLocked || !isIncluded

                                    return (
                                        <div
                                            key={token}
                                            className={cn(
                                                "flex items-center gap-1 px-2 py-1 rounded-md border text-[10px] font-bold transition-all shadow-sm dark:shadow-none",
                                                !tokenLocked
                                                    ? getTokenColor(token)
                                                    : "bg-black/5 dark:bg-black/20 border-black/5 dark:border-white/5 text-muted-foreground/50"
                                            )}
                                        >
                                            {tokenLocked && <Lock className="w-2 h-2 opacity-50" />}
                                            {token}
                                        </div>
                                    )
                                })}
                            </div>

                            {/* Action Footer */}
                            <div className="pt-3 mt-1 border-t border-black/5 dark:border-white/5">
                                {isLocked ? (
                                    <Button className="w-full bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 text-muted-foreground border border-black/5 dark:border-white/5 hover:border-black/10 dark:hover:border-white/10 shadow-none h-10 flex justify-between group/btn">
                                        <span className="flex items-center gap-2 text-xs">
                                            <Lock className="w-3.5 h-3.5" />
                                            <span className="bg-gradient-to-r from-neutral-500 to-neutral-700 dark:from-neutral-200 dark:to-neutral-400 bg-clip-text text-transparent font-bold">
                                                Locked Feature
                                            </span>
                                        </span>
                                        <Link href="/pricing" className={cn("text-[10px] font-bold px-2 py-1 rounded bg-gradient-to-r text-white shadow-md", theme.bgGradient)}>
                                            UPGRADE
                                        </Link>
                                    </Button>
                                ) : (
                                    <Button
                                        variant="ghost"
                                        className="w-full h-12 flex justify-between items-center group/btn hover:bg-black/5 dark:hover:bg-white/5 px-3" // Increased height to h-12
                                        onClick={() => setShowDetails(true)}
                                    >
                                        <span className="text-xs font-medium text-muted-foreground group-hover/btn:text-foreground transition-colors">
                                            View Performance Details
                                        </span>
                                        <span className={cn("p-1.5 rounded-full bg-black/5 dark:bg-black/20 transition-all group-hover/btn:scale-110", theme.accent)}>
                                            <ArrowUpRight className="w-3.5 h-3.5" />
                                        </span>
                                    </Button>
                                )}
                            </div>
                        </div>

                    </CardContent>
                </Card>
            </div>

            <StrategyDetailsModal
                offering={selectedVariant}
                variants={sortedVariants}
                open={showDetails}
                onOpenChange={setShowDetails}
            />
        </>
    )
}
