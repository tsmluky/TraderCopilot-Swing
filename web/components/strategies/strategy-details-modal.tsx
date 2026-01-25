'use client'

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import { CheckCircle2, TrendingUp, Activity, BarChart3, AlertTriangle, Lock } from "lucide-react"
import type { StrategyOffering } from "./master-strategy-card"

interface StrategyDetailsModalProps {
    offering: StrategyOffering | null
    open: boolean
    onOpenChange: (open: boolean) => void
}

export function StrategyDetailsModal({ offering, open, onOpenChange }: StrategyDetailsModalProps) {
    if (!offering) return null

    // Mock description data based on strategy code (since backend doesn't send rich text yet)
    // In a real app, this would come from the API.
    const details = getStrategyDetails(offering.strategy_code)

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-2xl bg-card border-border shadow-2xl">
                <DialogHeader>
                    <div className="flex items-center gap-3 mb-2">
                        <DialogTitle className="text-2xl font-bold flex items-center gap-3">
                            {offering.strategy_name}
                            <Badge variant="outline" className="text-sm font-medium">
                                {offering.timeframe}
                            </Badge>
                        </DialogTitle>
                        {offering.locked && (
                            <Badge variant="secondary" className="gap-1">
                                <Lock className="w-3 h-3" /> Locked
                            </Badge>
                        )}
                    </div>
                    <DialogDescription className="text-base text-muted-foreground">
                        {details.shortDescription}
                    </DialogDescription>
                </DialogHeader>

                <ScrollArea className="max-h-[60vh] pr-4">
                    <div className="space-y-6 py-4">
                        {/* Key Stats Grid */}
                        <div className="grid grid-cols-3 gap-4">
                            <div className="p-4 rounded-xl bg-secondary/20 border border-border flex flex-col items-center text-center">
                                <TrendingUp className="w-5 h-5 text-emerald-500 mb-2" />
                                <span className="text-xs text-muted-foreground uppercase font-semibold">Win Rate (Est)</span>
                                <span className="text-xl font-bold text-foreground">{details.stats.winRate}</span>
                            </div>
                            <div className="p-4 rounded-xl bg-secondary/20 border border-border flex flex-col items-center text-center">
                                <Activity className="w-5 h-5 text-blue-500 mb-2" />
                                <span className="text-xs text-muted-foreground uppercase font-semibold">Signal Freq</span>
                                <span className="text-xl font-bold text-foreground">{details.stats.frequency}</span>
                            </div>
                            <div className="p-4 rounded-xl bg-secondary/20 border border-border flex flex-col items-center text-center">
                                <AlertTriangle className="w-5 h-5 text-amber-500 mb-2" />
                                <span className="text-xs text-muted-foreground uppercase font-semibold">Risk Level</span>
                                <span className="text-xl font-bold text-foreground">{details.stats.risk}</span>
                            </div>
                        </div>

                        <Separator />

                        {/* How it works */}
                        <div className="space-y-3">
                            <h3 className="text-lg font-semibold flex items-center gap-2">
                                <BarChart3 className="w-5 h-5 text-primary" />
                                How it works
                            </h3>
                            <p className="text-sm leading-relaxed text-muted-foreground">
                                {details.longDescription}
                            </p>
                            <ul className="grid gap-2 mt-2">
                                {details.features.map((feature, i) => (
                                    <li key={i} className="flex items-start gap-2 text-sm text-foreground/80">
                                        <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                                        {feature}
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <Separator />

                        {/* Ideal For */}
                        <div className="space-y-3">
                            <h3 className="text-lg font-semibold">Ideal For</h3>
                            <p className="text-sm text-muted-foreground">
                                {details.idealFor}
                            </p>
                        </div>
                    </div>
                </ScrollArea>

                <DialogFooter>
                    {offering.locked && offering.locked_reason === 'UPGRADE_REQUIRED' && (
                        <Button className="bg-primary text-primary-foreground hover:bg-primary/90 w-full sm:w-auto" onClick={() => window.location.href = '/pricing'}>
                            Upgrade to Unlock
                        </Button>
                    )}
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}

// --- MOCK DATA GENERATOR (Premium Feel) ---
function getStrategyDetails(code: string) {
    if (code === 'TITAN_BREAKOUT') {
        return {
            shortDescription: "High-volatility breakout system designed to capture explosive moves in crypto markets.",
            longDescription: "Titan Breakout monitors price compression zones and volatility contractions. When momentum ignites, it triggers entries on confirmed breakouts, riding the wave until exhaustion. It uses dynamic stops to protect profits.",
            stats: {
                winRate: "68%",
                frequency: "Medium",
                risk: "Moderate"
            },
            features: [
                "Identifies consolidation patterns (Flags, Pennants)",
                "Filters out false breakouts using volume confirmation",
                "Dynamic trailing stop-loss to maximize run-up",
                "Best performance during high-volatility expansions"
            ],
            idealFor: "Traders looking for aggressive growth during trending markets."
        }
    }
    if (code === 'FLOW_MASTER') {
        return {
            shortDescription: "Trend-following momentum engine that surfs institutional liquidity flows.",
            longDescription: "Flow Master analyzes multi-timeframe alignment to detect sustained institutional buying or selling pressure. It enters on pullbacks within established trends, offering high R:R ratios by aligning with the dominant market force.",
            stats: {
                winRate: "75%",
                frequency: "Low - Medium",
                risk: "Low"
            },
            features: [
                "Multi-timeframe trend alignment (HTF confirmation)",
                "Pullback entries to minimize drawdown",
                "Volume delta analysis for flow confirmation",
                "Higher win-rate, steady growth focus"
            ],
            idealFor: "Conservative traders seeking consistent returns with lower drawdowns."
        }
    }
    // Default
    return {
        shortDescription: "Advanced algorithmic trading strategy.",
        longDescription: "Uses statistical analysis to find edge cases in the market.",
        stats: { winRate: "--", frequency: "--", risk: "--" },
        features: ["Algorithmic execution", "Risk management"],
        idealFor: "Swing traders."
    }
}
