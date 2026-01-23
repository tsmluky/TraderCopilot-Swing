'use client'

import { TrendingUp, Activity, Clock, Layers } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { cn } from '@/lib/utils'
import type { Strategy } from '@/lib/types'

interface StrategyCardProps {
    strategy: Strategy
    onToggle: (id: string, currentStatus: boolean) => void
    isToggling?: boolean
}

export function StrategyCard({ strategy, onToggle, isToggling }: StrategyCardProps) {
    // Helper for token colors
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

    return (
        <Card className={cn(
            "group relative overflow-hidden border-border bg-gradient-to-br from-card to-card/50 transition-all hover:shadow-md hover:border-primary/20",
            strategy.isActive ? "ring-1 ring-primary/20" : ""
        )}>
            <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                    <div className="space-y-1.5 flex-1">
                        <CardTitle className="text-xl font-semibold tracking-tight text-foreground flex items-center gap-2">
                            {strategy.name}
                        </CardTitle>
                        <CardDescription className="line-clamp-2 text-xs text-muted-foreground/80 h-8">
                            {strategy.description}
                        </CardDescription>
                    </div>

                    <div className="flex flex-col items-end gap-1">
                        <Switch
                            checked={strategy.isActive}
                            onCheckedChange={() => onToggle(strategy.id, strategy.isActive)}
                            disabled={isToggling}
                            className="data-[state=checked]:bg-primary"
                        />
                        <span className="text-[10px] text-muted-foreground">
                            {strategy.isActive ? 'Active' : 'Paused'}
                        </span>
                    </div>
                </div>
            </CardHeader>

            <CardContent className="space-y-5">
                {/* Chips/Tags for Tokens & Timeframes */}
                <div className="flex flex-wrap gap-2">
                    {/* Tokens */}
                    {strategy.tokens.map(token => (
                        <Badge
                            key={token}
                            variant="outline"
                            className={cn("text-[10px] px-2 py-0.5 pointer-events-none", getTokenColor(token))}
                        >
                            {token}
                        </Badge>
                    ))}

                    {/* Timeframes */}
                    {strategy.timeframes.map(tf => (
                        <Badge key={tf} variant="secondary" className="text-[10px] px-2 py-0.5 bg-secondary/50 text-muted-foreground border-border/50">
                            <Clock className="w-3 h-3 mr-1 opacity-70" /> {tf}
                        </Badge>
                    ))}
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-3 gap-2 py-3 bg-secondary/20 rounded-lg border border-border/50 px-3">
                    <div className="space-y-0.5">
                        <span className="text-[10px] uppercase text-muted-foreground font-medium flex items-center gap-1">
                            <Activity className="h-3 w-3" /> Win Rate
                        </span>
                        <div className={cn("text-lg font-bold tabular-nums", strategy.winRate > 50 ? "text-green-500" : "text-foreground")}>
                            {strategy.winRate}%
                        </div>
                    </div>

                    <div className="space-y-0.5">
                        <span className="text-[10px] uppercase text-muted-foreground font-medium flex items-center gap-1">
                            <TrendingUp className="h-3 w-3" /> ROI
                        </span>
                        <div className="text-lg font-bold tabular-nums text-foreground">
                            {strategy.avgReturn}%
                        </div>
                    </div>

                    <div className="space-y-0.5">
                        <span className="text-[10px] uppercase text-muted-foreground font-medium flex items-center gap-1">
                            <Layers className="h-3 w-3" /> Signals
                        </span>
                        <div className="text-lg font-bold tabular-nums text-foreground">
                            {strategy.signals}
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}
