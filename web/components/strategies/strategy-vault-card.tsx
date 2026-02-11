"use client"

import { useState, useMemo } from "react"
import { TrendingUp, Lock, Activity, Clock, Zap, Waves, BrainCircuit, Power } from "lucide-react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"
import Link from "next/link"
import { StrategyDetailsModal } from "./strategy-details-modal"

// Reusing the interface
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

interface StrategyVaultCardProps {
    strategyName: string
    strategyCode: string
    description: string
    variants: StrategyOffering[]
    isEnabled: boolean
    onToggle: (enabled: boolean) => void
}

export function StrategyVaultCard({
    strategyName,
    strategyCode,
    description,
    variants,
    isEnabled,
    onToggle
}: StrategyVaultCardProps) {
    // Sort variants by timeframe logic (1H -> 4H) and exclude 1D if needed
    const sortedVariants = useMemo(() => {
        const order = ["1H", "4H", "1D", "1W"]
        return [...variants]
            .filter(v => v.timeframe !== '1D')
            .sort((a, b) => {
                return order.indexOf(a.timeframe) - order.indexOf(b.timeframe)
            })
    }, [variants])

    const defaultVariant = sortedVariants.find(v => !v.locked) || sortedVariants[0]
    const [selectedVariant, setSelectedVariant] = useState<StrategyOffering>(defaultVariant)
    const [showDetails, setShowDetails] = useState(false)

    // THEME LOGIC - Dark/Neon Vault Style
    const theme = useMemo(() => {
        if (strategyCode === 'DONCHIAN_V2') {
            return {
                accent: "text-orange-500",
                bgGradient: "from-orange-500/5 to-transparent",
                border: "border-orange-500/20",
                shadow: "shadow-orange-500/10",
                icon: <Zap className="w-5 h-5" />,
                glow: "bg-orange-500"
            }
        } else if (strategyCode === 'SUPER_TREND') {
            return {
                accent: "text-emerald-500",
                bgGradient: "from-emerald-500/5 to-transparent",
                border: "border-emerald-500/20",
                shadow: "shadow-emerald-500/10",
                icon: <TrendingUp className="w-5 h-5" />,
                glow: "bg-emerald-500"
            }
        } else if (strategyCode === 'MEAN_REVERSION_V1' || strategyCode === 'MEAN_REVERSION') {
            return {
                accent: "text-purple-500",
                bgGradient: "from-purple-500/5 to-transparent",
                border: "border-purple-500/20",
                shadow: "shadow-purple-500/10",
                icon: <BrainCircuit className="w-5 h-5" />,
                glow: "bg-purple-500"
            }
        } else {
            // Trend Surfer / SMA
            return {
                accent: "text-cyan-500",
                bgGradient: "from-cyan-500/5 to-transparent",
                border: "border-cyan-500/20",
                shadow: "shadow-cyan-500/10",
                icon: <Waves className="w-5 h-5" />,
                glow: "bg-cyan-500"
            }
        }
    }, [strategyCode])

    // Token Colors Helper (muted versions for vault)
    const getTokenStyle = (t: string) => {
        switch (t.toUpperCase()) {
            case 'BTC': return 'text-orange-400 border-orange-500/30 bg-orange-500/5'
            case 'ETH': return 'text-indigo-400 border-indigo-500/30 bg-indigo-500/5'
            case 'SOL': return 'text-teal-400 border-teal-500/30 bg-teal-500/5'
            case 'BNB': return 'text-yellow-400 border-yellow-500/30 bg-yellow-500/5'
            case 'XRP': return 'text-blue-400 border-blue-500/30 bg-blue-500/5'
            default: return 'text-zinc-400 border-zinc-700 bg-zinc-800/50'
        }
    }

    if (!selectedVariant) return null

    const isLocked = selectedVariant.locked

    return (
        <>
            <div className={cn(
                "group relative transition-all duration-500",
                !isEnabled && "opacity-70 grayscale-[0.5]"
            )}>
                {/* Connector Lines (Decorative) */}
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 w-px h-3 bg-gradient-to-b from-transparent to-zinc-800 hidden md:block" />

                {/* Main Vault Module */}
                <Card className={cn(
                    "relative overflow-hidden border-2 transition-all duration-300 bg-zinc-950/80 backdrop-blur-xl",
                    isEnabled
                        ? cn(theme.border, "hover:border-opacity-50 hover:shadow-2xl", theme.shadow)
                        : "border-zinc-800/50 bg-zinc-950/50"
                )}>

                    {/* Active Status Indicator Line - Top */}
                    <div className={cn(
                        "absolute top-0 left-0 right-0 h-[2px] w-full transition-all duration-700",
                        isEnabled ? theme.glow : "bg-zinc-800",
                        isEnabled ? "opacity-100 shadow-[0_0_10px_currentColor] text-" + theme.glow.replace('bg-', '') : "opacity-0"
                    )} />

                    {/* Gradient Background */}
                    <div className={cn(
                        "absolute inset-0 bg-gradient-to-br opacity-20 pointer-events-none transition-opacity duration-500",
                        theme.bgGradient,
                        !isEnabled && "opacity-0"
                    )} />

                    <CardHeader className="p-6 pb-2 relative z-10">
                        <div className="flex items-start justify-between gap-4">
                            <div className="flex items-center gap-4">
                                {/* Icon Module */}
                                <div className={cn(
                                    "w-12 h-12 rounded-xl flex items-center justify-center border shadow-inner transition-colors duration-300",
                                    isEnabled
                                        ? cn("bg-zinc-900 border-zinc-800", theme.accent)
                                        : "bg-zinc-900/50 border-zinc-800 text-zinc-600"
                                )}>
                                    {isLocked ? <Lock className="w-5 h-5" /> : theme.icon}
                                </div>

                                <div>
                                    <h3 className={cn(
                                        "font-bold text-lg tracking-tight flex items-center gap-2",
                                        isEnabled ? "text-zinc-100" : "text-zinc-500"
                                    )}>
                                        {strategyName}
                                        {isLocked && <Badge variant="outline" className="text-[10px] border-zinc-700 text-zinc-500 h-5">LOCKED</Badge>}
                                    </h3>
                                    <p className="text-xs text-zinc-500 font-medium leading-relaxed max-w-[220px]">
                                        {description}
                                    </p>
                                </div>
                            </div>

                            {/* Power Switch */}
                            <div className="flex flex-col items-end gap-2">
                                <Switch
                                    checked={isEnabled}
                                    onCheckedChange={onToggle}
                                    disabled={isLocked}
                                    className={cn(
                                        "data-[state=checked]:bg-zinc-100 data-[state=unchecked]:bg-zinc-900 border-2 border-zinc-800",
                                        isEnabled && "data-[state=checked]:shadow-[0_0_15px_rgba(255,255,255,0.3)]"
                                    )}
                                />
                                <span className={cn(
                                    "text-[9px] font-mono uppercase tracking-widest",
                                    isEnabled ? theme.accent : "text-zinc-700"
                                )}>
                                    {isEnabled ? "ONLINE" : "OFFLINE"}
                                </span>
                            </div>
                        </div>
                    </CardHeader>

                    <CardContent className="p-6 pt-4 relative z-10 space-y-6">

                        {/* Metrics Display Dashboard */}
                        <div className="grid grid-cols-3 gap-px bg-zinc-800/30 rounded-lg overflow-hidden border border-zinc-800/50">
                            {/* Win Rate */}
                            <div className="bg-zinc-900/50 p-3 flex flex-col items-center justify-center group/metric hover:bg-zinc-900/80 transition-colors">
                                <span className="text-[9px] text-zinc-500 font-mono uppercase tracking-wider mb-1 group-hover/metric:text-zinc-400">Win Rate</span>
                                <span className={cn(
                                    "text-lg font-mono font-bold tabular-nums",
                                    isLocked ? "text-zinc-700 blur-[2px]" : (isEnabled ? theme.accent : "text-zinc-600")
                                )}>
                                    {selectedVariant.win_rate || "--%"}
                                </span>
                            </div>

                            {/* ROI/Signals */}
                            <div className="bg-zinc-900/50 p-3 flex flex-col items-center justify-center group/metric hover:bg-zinc-900/80 transition-colors">
                                <span className="text-[9px] text-zinc-500 font-mono uppercase tracking-wider mb-1 group-hover/metric:text-zinc-400">Signals</span>
                                <span className={cn(
                                    "text-lg font-mono font-bold tabular-nums",
                                    isLocked ? "text-zinc-700 blur-[2px]" : "text-zinc-300"
                                )}>
                                    {selectedVariant.total_signals || 0}
                                </span>
                            </div>

                            {/* Timeframe */}
                            <div className="bg-zinc-900/50 p-3 flex flex-col items-center justify-center group/metric hover:bg-zinc-900/80 transition-colors">
                                <span className="text-[9px] text-zinc-500 font-mono uppercase tracking-wider mb-1 group-hover/metric:text-zinc-400">Cadence</span>
                                <span className="text-xs font-mono font-bold text-zinc-300">
                                    {selectedVariant.timeframe}
                                </span>
                            </div>
                        </div>

                        {/* Market Coverage */}
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <span className="text-[10px] text-zinc-600 font-bold uppercase tracking-widest flex items-center gap-1.5">
                                    <Activity className="w-3 h-3" /> Coverage
                                </span>
                            </div>

                            <div className="flex flex-wrap gap-2">
                                {(selectedVariant.all_tokens || selectedVariant.tokens).map(token => {
                                    const active = selectedVariant.tokens.includes(token)
                                    const locked = isLocked || !active

                                    return (
                                        <div key={token} className={cn(
                                            "px-2 py-1 rounded text-[10px] font-mono font-bold border flex items-center gap-1.5 transition-all",
                                            locked
                                                ? "text-zinc-700 border-zinc-800 bg-zinc-900/50"
                                                : getTokenStyle(token)
                                        )}>
                                            {locked && <Lock className="w-2 h-2" />}
                                            {token}
                                        </div>
                                    )
                                })}
                            </div>
                        </div>

                        {/* Footer Action */}
                        <div className="pt-2">
                            {isLocked ? (
                                <Link href="/pricing" className="block">
                                    <button className="w-full py-2.5 rounded-lg border border-zinc-800 bg-zinc-900/50 text-zinc-500 text-xs font-bold hover:bg-zinc-900 hover:text-zinc-300 transition-all flex items-center justify-center gap-2 group/btn">
                                        <Lock className="w-3 h-3 group-hover/btn:text-white transition-colors" />
                                        UNLOCK MODULE
                                    </button>
                                </Link>
                            ) : (
                                <button
                                    onClick={() => setShowDetails(true)}
                                    className="w-full py-2.5 rounded-lg border border-zinc-800 bg-zinc-900/50 text-zinc-400 text-xs font-bold hover:bg-zinc-800 hover:text-zinc-200 transition-all hover:border-zinc-700 flex items-center justify-center gap-2"
                                >
                                    VIEW ANALYTICS
                                </button>
                            )}
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
