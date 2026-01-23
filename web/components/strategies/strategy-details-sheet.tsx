'use client'

import { useState, useEffect } from 'react'
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
} from '@/components/ui/sheet'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { strategiesService } from '@/services/strategies'
import type { Strategy, Signal } from '@/lib/types'
import { ArrowRight, Calendar, CheckCircle, TrendingUp, XCircle, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StrategyDetailsSheetProps {
    strategy: Strategy | null
    isOpen: boolean
    onClose: () => void
}

export function StrategyDetailsSheet({ strategy, isOpen, onClose }: StrategyDetailsSheetProps) {
    const [history, setHistory] = useState<any[]>([])
    const [isLoading, setIsLoading] = useState(false)

    useEffect(() => {
        if (isOpen && strategy) {
            loadHistory(strategy.id)
        }
    }, [isOpen, strategy])

    const loadHistory = async (id: string) => {
        try {
            setIsLoading(true)
            const data = await strategiesService.getHistory(id)
            setHistory(Array.isArray(data) ? data : [])
        } catch (e) {
            console.error(e)
        } finally {
            setIsLoading(false)
        }
    }

    if (!strategy) return null

    return (
        <Sheet open={isOpen} onOpenChange={(open) => !open && onClose()}>
            <SheetContent className="w-[400px] sm:w-[600px] border-l border-border/50 bg-background/95 backdrop-blur-xl p-0 shadow-2xl flex flex-col h-full">
                <div className="p-8 pb-0">
                    <SheetHeader className="mb-6 space-y-4">
                        <div className="flex items-center gap-3">
                            <Badge variant="outline" className="text-primary border-primary/20 bg-primary/5">
                                {strategy.symbol || strategy.tokens?.[0] || 'MULTI'}
                            </Badge>
                            <span className="text-xs text-muted-foreground font-mono uppercase">
                                {strategy.timeframes?.[0] || '1d'}
                            </span>
                        </div>

                        <SheetTitle className="text-2xl font-bold tracking-tight">{strategy.name}</SheetTitle>
                        <SheetDescription className="text-base text-muted-foreground leading-relaxed">
                            {strategy.description}
                        </SheetDescription>
                    </SheetHeader>
                </div>

                <div className="flex-1 overflow-hidden px-8 pb-8">
                    <ScrollArea className="h-full pr-4">
                        <div className="space-y-10 pb-10">
                            {/* Logic Explanation Section */}
                            <div className="space-y-3">
                                <h4 className="text-sm font-medium text-foreground uppercase tracking-wider">How it works</h4>
                                <div className="p-4 rounded-lg bg-secondary/20 border border-border/50 text-sm leading-6 text-muted-foreground/90">
                                    <p>
                                        This strategy continuously monitors market structure using
                                        <strong className="text-foreground"> price action analysis</strong> and
                                        <strong className="text-foreground"> proprietary indicators</strong>.
                                    </p>
                                    <ul className="mt-3 space-y-2 list-disc list-inside opacity-80">
                                        <li>Entries are triggered on confirmed trend reversals or breakouts.</li>
                                        <li>Risk is managed with dynamic Stop Losses based on volatility (ATR).</li>
                                        <li>Exits occur at technical targets or when trend momentum fades.</li>
                                    </ul>
                                </div>
                            </div>

                            {/* Recent Activity */}
                            <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                    <h4 className="text-sm font-medium text-foreground uppercase tracking-wider">Recent Signals</h4>
                                    {isLoading && <span className="text-xs text-muted-foreground animate-pulse">Syncing...</span>}
                                </div>

                                <div>
                                    <div className="space-y-3">
                                        {history.length === 0 && !isLoading && (
                                            <div className="py-8 text-center text-muted-foreground italic text-sm border border-dashed border-border rounded-lg">
                                                No signals recorded recently.
                                            </div>
                                        )}

                                        {history.map((sig) => (
                                            <div key={sig.id} className="group flex flex-col gap-2 p-3 rounded-lg border border-border/40 bg-card/30 hover:bg-card/60 transition-colors">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap-2">
                                                        <Badge variant={sig.direction === 'LONG' ? 'default' : 'destructive'} className="h-5 px-1.5 text-[10px]">
                                                            {sig.direction}
                                                        </Badge>
                                                        <span className="text-xs font-mono text-muted-foreground">
                                                            {new Date(sig.timestamp).toLocaleDateString()}
                                                        </span>
                                                    </div>

                                                    {sig.result ? (
                                                        <Badge variant="outline" className={cn("h-5 text-[10px]",
                                                            sig.result.result === 'WIN' ? 'border-success text-success bg-success/10' : 'border-destructive text-destructive bg-destructive/10'
                                                        )}>
                                                            {sig.result.result} {sig.result.pnl_r && `(${sig.result.pnl_r}R)`}
                                                        </Badge>
                                                    ) : (
                                                        <span className="text-[10px] text-muted-foreground italic">Active</span>
                                                    )}
                                                </div>

                                                <div className="grid grid-cols-2 gap-4 text-xs">
                                                    <div>
                                                        <span className="text-muted-foreground/60">Entry:</span>
                                                        <span className="ml-1 font-mono text-foreground">${sig.entry}</span>
                                                    </div>
                                                    {sig.result?.exit_price && (
                                                        <div className="text-right">
                                                            <span className="text-muted-foreground/60">Exit:</span>
                                                            <span className="ml-1 font-mono text-foreground">${sig.result.exit_price}</span>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </ScrollArea>
                </div>
            </SheetContent >
        </Sheet >
    )
}
