"use client"

import { useState, useMemo } from "react"
import { TrendingUp, Lock, ArrowUpRight, Clock, Zap, Activity, Waves, BrainCircuit, Power, Cpu, Gauge, Radio, Signal } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"
import Link from "next/link"
import { StrategyDetailsModal } from "./strategy-details-modal"

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

interface StrategyStackModuleProps {
    strategyName: string
    strategyCode: string
    description: string
    variants: StrategyOffering[]
    isEnabled: boolean
    onToggle: (enabled: boolean) => void
    isLast?: boolean
}

interface StrategyTheme {
    accent: string
    bgGradient: string
    border: string
    shadow: string
    bar: string
    icon: string
    bgActive: string
}

export function StrategyStackModule({
    strategyName,
    strategyCode,
    description,
    variants,
    isEnabled,
    onToggle,
    isLast
}: StrategyStackModuleProps) {
    const sortedVariants = useMemo(() => {
        const order = ["1H", "4H", "1D", "1W"]
        return [...variants]
            .filter(v => v.timeframe !== '1D')
            .sort((a, b) => order.indexOf(a.timeframe) - order.indexOf(b.timeframe))
    }, [variants])

    const defaultVariant = sortedVariants.find(v => !v.locked) || sortedVariants[0]
    const [selectedVariant, setSelectedVariant] = useState<StrategyOffering>(defaultVariant)
    const [showDetails, setShowDetails] = useState(false)

    // THEME LOGIC - High-End Fintech / Cinematic
    const theme = useMemo<StrategyTheme>(() => {
        if (strategyCode === 'DONCHIAN_V2') {
            return {
                accent: "text-orange-600 dark:text-orange-500",
                bgGradient: "from-orange-500/30 to-transparent",
                border: "border-orange-500 dark:border-orange-500/20",
                shadow: "shadow-[0_4px_12px_-2px_rgba(249,115,22,0.4)] dark:shadow-[0_0_20px_-5px_rgba(249,115,22,0.15)]",
                bar: "bg-orange-600 dark:bg-orange-500",
                icon: "text-orange-600 dark:text-orange-400",
                bgActive: "bg-orange-50 dark:bg-background"
            }
        } else if (strategyCode === 'SUPER_TREND') {
            return {
                accent: "text-emerald-600 dark:text-emerald-500",
                bgGradient: "from-emerald-500/30 to-transparent",
                border: "border-emerald-500 dark:border-emerald-500/20",
                shadow: "shadow-[0_4px_12px_-2px_rgba(16,185,129,0.4)] dark:shadow-[0_0_20px_-5px_rgba(16,185,129,0.15)]",
                bar: "bg-emerald-600 dark:bg-emerald-500",
                icon: "text-emerald-600 dark:text-emerald-400",
                bgActive: "bg-emerald-50 dark:bg-background"
            }
        } else if (strategyCode === 'MEAN_REVERSION_V1' || strategyCode === 'MEAN_REVERSION') {
            return {
                accent: "text-purple-600 dark:text-purple-500",
                bgGradient: "from-purple-500/30 to-transparent",
                border: "border-purple-500 dark:border-purple-500/20",
                shadow: "shadow-[0_4px_12px_-2px_rgba(168,85,247,0.4)] dark:shadow-[0_0_20px_-5px_rgba(168,85,247,0.15)]",
                bar: "bg-purple-600 dark:bg-purple-500",
                icon: "text-purple-600 dark:text-purple-400",
                bgActive: "bg-purple-50 dark:bg-background"
            }
        } else {
            return {
                accent: "text-cyan-600 dark:text-cyan-500",
                bgGradient: "from-cyan-500/30 to-transparent",
                border: "border-cyan-500 dark:border-cyan-500/20",
                shadow: "shadow-[0_4px_12px_-2px_rgba(6,182,212,0.4)] dark:shadow-[0_0_20px_-5px_rgba(6,182,212,0.15)]",
                bar: "bg-cyan-600 dark:bg-cyan-500",
                icon: "text-cyan-600 dark:text-cyan-400",
                bgActive: "bg-cyan-50 dark:bg-background"
            }
        }
    }, [strategyCode])

    const isLocked = selectedVariant.locked

    const handleToggle = (e: React.MouseEvent) => {
        e.stopPropagation()
        if (!isLocked) {
            onToggle(!isEnabled)
        }
    }

    return (
        <>
            <div className={cn(
                "group relative w-full transition-all duration-500",
                !isEnabled && "opacity-70 grayscale-[0.6] hover:opacity-90 hover:grayscale-[0.4]"
            )}>
                {/* Connecting Bus Line (Left - Compact) */}
                {!isLast && (
                    <div className="absolute left-8 top-10 bottom-[-16px] w-[1px] bg-gradient-to-b from-border/50 via-border/20 to-border/5 z-0" />
                )}

                <div className="relative z-10 flex items-stretch gap-0 p-0 rounded-xl transition-all duration-500">

                    {/* 1. Status Core (Power Button Only) */}
                    <div
                        className="flex flex-col items-center justify-center py-3 pl-2 pr-4 cursor-pointer z-20 relative"
                        onClick={handleToggle}
                        title={isEnabled ? "Deactivate Module" : "Activate Module"}
                    >
                        {/* Power Button Container */}
                        <div className={cn(
                            "w-12 h-12 rounded-xl flex items-center justify-center border transition-all duration-300 shadow-sm relative overflow-hidden group/power",
                            isEnabled
                                ? cn(theme.bgActive, theme.border, theme.shadow)
                                : "bg-white border-zinc-200 hover:border-zinc-300 dark:bg-card/40 dark:border-border/30 dark:hover:bg-card/60 dark:hover:border-border/60"
                        )}>
                            {/* Inner Glow for Active State */}
                            {isEnabled && (
                                <div className={cn("absolute inset-0 opacity-20 bg-gradient-to-br", theme.bgGradient)} />
                            )}

                            <Power className={cn(
                                "w-5 h-5 transition-all duration-300",
                                isEnabled ? theme.icon : "text-zinc-300 group-hover/power:text-zinc-400 dark:text-muted-foreground/40 dark:group-hover/power:text-foreground"
                            )} />
                        </div>
                    </div>

                    {/* 2. Main Module Body (Compact Blade) */}
                    <div className={cn(
                        "flex-1 flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 my-1 mr-1 rounded-xl border transition-all duration-300 cursor-pointer group/card relative overflow-hidden",
                        isEnabled
                            ? cn("bg-card/40 backdrop-blur-sm border-border/40 hover:border-border/80 hover:bg-card/60 hover:shadow-lg", theme.border)
                            : "bg-card/10 border-border/10 hover:bg-card/20 hover:border-border/30"
                    )}
                        onClick={() => !isLocked && setShowDetails(true)}
                    >
                        {/* Background Subtle Gradient */}
                        {isEnabled && (
                            <div className={cn("absolute inset-0 opacity-[0.03] bg-gradient-to-r", theme.bgGradient)} />
                        )}

                        {/* Info Section */}
                        <div className="flex-1 min-w-[200px] relative">
                            <div className="flex items-center gap-3 mb-1.5">
                                <h3 className={cn(
                                    "font-bold text-lg tracking-tight transition-colors duration-300",
                                    isEnabled ? "text-foreground" : "text-muted-foreground"
                                )}>
                                    {strategyName}
                                </h3>
                                {isLocked && <Badge variant="outline" className="text-[9px] uppercase font-bold tracking-widest border-muted text-muted-foreground px-1.5 py-0">Locked</Badge>}
                                {!isLocked && isEnabled && (
                                    <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-background/50 border border-border/50 shadow-sm">
                                        <div className={cn("w-1 h-1 rounded-full animate-pulse", theme.bar)} />
                                        <span className={cn("text-[9px] font-bold tracking-widest uppercase", theme.accent)}>Active</span>
                                    </div>
                                )}
                            </div>
                            <p className="text-xs text-muted-foreground/80 font-medium leading-relaxed max-w-lg line-clamp-1">
                                {description}
                            </p>
                        </div>

                        {/* Metrics Panel (Compact Glass) */}
                        <div className="flex items-center gap-6 px-4 py-2 rounded-lg bg-background/20 border border-border/10 backdrop-blur-sm shadow-inner group-hover/card:bg-background/40 transition-all">

                            {/* Win Rate */}
                            <div className="flex flex-col items-start gap-0.5 min-w-[70px]">
                                <span className="text-[9px] font-bold uppercase tracking-widest opacity-60">Win Rate</span>
                                <span className={cn(
                                    "text-lg font-mono font-bold tabular-nums tracking-tight",
                                    isLocked ? "text-muted blur-sm" : (isEnabled ? theme.accent : "text-foreground")
                                )}>
                                    {selectedVariant.win_rate || "--%"}
                                </span>
                            </div>

                            <div className="w-[1px] h-6 bg-border/20" />

                            {/* Signals */}
                            <div className="flex flex-col items-start gap-0.5 min-w-[60px]">
                                <span className="text-[9px] font-bold uppercase tracking-widest opacity-60">Signals</span>
                                <span className={cn(
                                    "text-lg font-mono font-bold tabular-nums tracking-tight",
                                    isLocked ? "text-muted blur-sm" : "text-foreground"
                                )}>
                                    {selectedVariant.total_signals || 0}
                                </span>
                            </div>

                        </div>

                        {/* Action Arrow (Subtle) */}
                        <div className={cn(
                            "w-8 h-8 rounded-full flex items-center justify-center border border-transparent transition-all duration-300",
                            isEnabled ? "group-hover/card:bg-background group-hover/card:border-border group-hover/card:shadow-md text-muted-foreground" : "opacity-0"
                        )}>
                            <ArrowUpRight className="w-4 h-4" />
                        </div>

                    </div>
                </div>
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
