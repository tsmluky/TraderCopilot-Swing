'use client'

import { useState } from 'react'
import { TrendingUp, Lock } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from '@/lib/utils'
import { ArrowUpRight } from 'lucide-react'
import Link from 'next/link'
import type { Strategy } from '@/lib/types' // Might need update? Strategy type is lenient.
import { StrategyDetailsModal } from './strategy-details-modal'

// We need to define the Offering interface locally or import it if we updated types.
// For now, we assume 'Strategy' type roughly matches what we return, 
// or we adapt the component to 'StrategyOffering'.

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
    // Stats (optional - if backend adds them later)
    win_rate?: string
    total_signals?: number
}

interface MasterStrategyCardProps {
    offering: StrategyOffering
    onRefresh?: () => void
}

export function MasterStrategyCard({ offering }: MasterStrategyCardProps) {
    // Modal State
    const [showDetails, setShowDetails] = useState(false)

    const isLocked = offering.locked

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

    // Stats Placeholders (Backend doesn't calculate them live yet for Offerings, 
    // or we might need to fetch them separately. For MVP, show 'Active' or '--')
    const winRateDisplay = offering.win_rate || '--'
    const signalsDisplay = offering.total_signals || 0

    return (
        <>
            <Card
                className={cn(
                    "group relative overflow-hidden transition-all cursor-pointer rounded-2xl",
                    isLocked
                        ? "bg-secondary/10 border-border opacity-70 hover:opacity-100"
                        : "bg-white border-black/5 shadow-sm hover:shadow-xl hover:shadow-primary/5 dark:bg-gradient-to-br dark:from-card dark:to-card/50 dark:border-primary/10 dark:hover:border-primary/30"
                )}
                onClick={() => setShowDetails(true)}
            >
                <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                        <div className="space-y-1.5 flex-1">
                            <div className="flex items-center gap-2">
                                <CardTitle className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
                                    {offering.strategy_name}
                                    <span className={cn(
                                        "text-xs px-2 py-0.5 rounded-md font-bold border",
                                        isLocked
                                            ? "bg-muted text-muted-foreground border-border"
                                            : "bg-primary/5 text-primary border-primary/10 dark:bg-primary/10 dark:border-primary/20"
                                    )}>
                                        {offering.timeframe}
                                    </span>
                                </CardTitle>
                            </div>
                            <CardDescription className="line-clamp-2 text-xs font-medium text-muted-foreground/80">
                                {/* Description implied? Or we can map codes to descriptions here if API doesn't send it */}
                                {offering.strategy_code === 'TITAN_BREAKOUT' ? "Breakout volatility system." : "Trend following momentum system."}
                            </CardDescription>
                        </div>

                        <div className="flex items-center gap-2">
                            {isLocked ? (
                                <Badge variant="outline" className="text-[10px] gap-1 border-muted bg-muted/50 text-muted-foreground">
                                    <Lock className="h-3 w-3" />
                                    {offering.locked_reason === 'UPGRADE_REQUIRED' ? 'PRO' : 'LOCKED'}
                                </Badge>
                            ) : (
                                <Badge variant="default" className="text-[10px] bg-emerald-500/10 text-emerald-600 dark:text-emerald-500 hover:bg-emerald-500/20 border-emerald-500/20 pointer-events-none shadow-none font-bold">
                                    Included
                                </Badge>
                            )}
                        </div>
                    </div>
                </CardHeader>

                <CardContent className="space-y-5">
                    {/* Tokens (Read Only Chips) */}
                    <div className="flex flex-wrap gap-2">
                        {/* Active Tokens */}
                        {offering.tokens.map((t, i) => (
                            <div
                                key={`active-${i}`}
                                className={cn(
                                    "flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-bold cursor-default transition-colors shadow-sm dark:shadow-none",
                                    isLocked
                                        ? "bg-muted/20 border-border text-muted-foreground opacity-60"
                                        : getTokenColor(t)
                                )}
                                onClick={(e) => e.stopPropagation()}
                            >
                                {t}
                            </div>
                        ))}

                        {/* Locked Tokens (Diff) */}
                        {(offering.all_tokens || []).filter(t => !offering.tokens.includes(t)).map((t, i) => (
                            <TooltipProvider key={`locked-${i}`}>
                                <Tooltip>
                                    <TooltipTrigger asChild>
                                        <div
                                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-dashed border-border bg-secondary/30 text-muted-foreground/50 text-xs font-medium cursor-not-allowed"
                                            onClick={(e) => e.stopPropagation()}
                                        >
                                            <Lock className="w-3 h-3 opacity-50" />
                                            {t}
                                        </div>
                                    </TooltipTrigger>
                                    <TooltipContent>
                                        <p>Available in Pro plan</p>
                                    </TooltipContent>
                                </Tooltip>
                            </TooltipProvider>
                        ))}
                    </div>

                    {/* Status Bar */}
                    <div className="grid grid-cols-3 gap-2 py-3 bg-secondary/20 dark:bg-secondary/10 rounded-xl border border-black/5 dark:border-border/50 px-3">
                        <div className="space-y-0.5">
                            <span className="text-[10px] uppercase text-muted-foreground font-bold tracking-wider">Status</span>
                            <div className={cn("text-sm font-black tabular-nums", isLocked ? "text-muted-foreground" : "text-emerald-600 dark:text-emerald-500")}>
                                {isLocked ? 'Locked' : 'Active'}
                            </div>
                        </div>

                        {/* Placeholder Stats */}
                        <div className="space-y-0.5">
                            <span className="text-[10px] uppercase text-muted-foreground font-bold tracking-wider">Win Rate</span>
                            <div className="text-sm font-black tabular-nums text-foreground/80">
                                {winRateDisplay}
                            </div>
                        </div>
                        <div className="space-y-0.5">
                            <span className="text-[10px] uppercase text-muted-foreground font-bold tracking-wider">Signals</span>
                            <div className="text-sm font-black tabular-nums text-foreground/80">
                                {signalsDisplay}
                            </div>
                        </div>
                    </div>

                    {/* Access Overlay or Footer */}
                    {isLocked && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/60 backdrop-blur-[1px] z-20 transition-opacity hover:bg-background/50">
                            {offering.locked_reason === 'UPGRADE_REQUIRED' && (
                                <Link href="/pricing" onClick={(e) => e.stopPropagation()}>
                                    <Badge className="cursor-pointer hover:scale-105 transition-transform bg-primary text-primary-foreground shadow-lg font-bold px-4 py-1.5 cursor-pointer">
                                        Upgrade Subscription
                                    </Badge>
                                </Link>
                            )}
                            {offering.locked_reason === 'TRIAL_EXPIRED' && (
                                <Badge variant="destructive" className="cursor-not-allowed opacity-90 font-bold">
                                    Trial Expired
                                </Badge>
                            )}
                        </div>
                    )}
                </CardContent>
            </Card>

            <StrategyDetailsModal
                offering={offering}
                open={showDetails}
                onOpenChange={setShowDetails}
            />
        </>
    )
}
