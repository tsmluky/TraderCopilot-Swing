'use client'

import { useState } from 'react'
import { TrendingUp, BarChart3, Clock, Lock } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { cn } from '@/lib/utils'
import { useAuth } from '@/context/auth-context'
import type { Strategy, Token } from '@/lib/types'
import { StrategyDetailsSheet } from './strategy-details-sheet'
import { ArrowUpRight } from 'lucide-react'
import { toast } from 'sonner'
import Link from 'next/link'
import { strategiesService } from '@/services/strategies'

interface MasterStrategyCardProps {
    name: string
    description?: string
    personas: Strategy[]
    onToggle: (id: string, targetStatus: boolean, newTimeframe?: string) => void
    isToggling?: boolean
    onRefresh?: () => void
    forcedTimeframe?: string
}

export function MasterStrategyCard({ name, description, personas, onToggle, isToggling, onRefresh, forcedTimeframe }: MasterStrategyCardProps) {
    const { canAccessTimeframe } = useAuth()

    // Sort personas by fixed token order: BTC, ETH, SOL, BNB, XRP
    const tokenOrder: Record<string, number> = { 'BTC': 1, 'ETH': 2, 'SOL': 3, 'BNB': 4, 'XRP': 5 }
    const sortedPersonas = [...personas].sort((a, b) => {
        const tA = (a.symbol || (a.tokens && a.tokens[0]) || '')
        const tB = (b.symbol || (b.tokens && b.tokens[0]) || '')
        return (tokenOrder[tA] || 99) - (tokenOrder[tB] || 99)
    })

    // State for active persona
    // Initialize with prioritized logic:
    // 1. First ACTIVE persona that Matches Forced Timeframe (Best case)
    // 2. First persona that Matches Forced Timeframe (Default for section)
    // 3. First ACTIVE persona (Fallback)
    // 4. Default first persona
    const [activePersonaId, setActivePersonaId] = useState<string>(() => {
        if (forcedTimeframe) {
            const contextActive = sortedPersonas.find(p => p.isActive && p.timeframes?.[0] === forcedTimeframe)
            if (contextActive) return contextActive.id

            const contextMatch = sortedPersonas.find(p => p.timeframes?.[0] === forcedTimeframe)
            if (contextMatch) return contextMatch.id
        }

        const active = sortedPersonas.find(p => p.isActive)
        return active ? active.id : (sortedPersonas[0]?.id || '')
    })

    const activePersona = sortedPersonas.find(p => p.id === activePersonaId) || sortedPersonas[0]

    if (!activePersona) return null

    // Check access based on active persona requirements
    // If forcedTimeframe, check that specific one. Otherwise check config.
    const timeframes = activePersona.timeframes || []
    const effectiveTimeframe = forcedTimeframe || timeframes[0] || '4h'

    const requiresPro = effectiveTimeframe.toLowerCase() === '1h'
    const hasAccess = !requiresPro || canAccessTimeframe('1H')

    // Contextual Active State
    // If forcedTimeframe is set, isActive requires (isActive=true AND configuredTimeframe == forcedTimeframe)
    // Compare case-insensitively just to be safe
    const isContextActive = activePersona.isActive && (!forcedTimeframe || (timeframes[0]?.toLowerCase() === forcedTimeframe.toLowerCase()))
    // Or should the toggle control just the *visible* one? 
    // User asked for "Cards with token selectors". Usually this means you select the token causing the card to update.
    // The Switch should probably control the *Active Persona*.

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

    // Display Vars
    const hasData = activePersona.winRate > 0 || activePersona.signals > 0
    const winRateDisplay = hasData ? `${activePersona.winRate}%` : '--'

    // Sheet State
    const [showDetails, setShowDetails] = useState(false)

    return (
        <>
            <Card className={cn(
                "group relative overflow-hidden border-border bg-gradient-to-br from-card to-card/50 transition-premium hover:shadow-premium-md hover:border-primary/20",
                isContextActive ? "ring-1 ring-primary/20" : ""
            )}>
                <CardHeader
                    className="pb-3 cursor-pointer hover:bg-muted/10 transition-colors"
                    onClick={() => setShowDetails(true)}
                >
                    <div className="flex items-start justify-between">
                        <div className="space-y-1.5 flex-1">
                            <div>
                                <CardTitle className="text-xl font-semibold tracking-tight text-foreground flex items-center gap-2">
                                    {name}
                                    <ArrowUpRight className="h-4 w-4 text-muted-foreground/50" />
                                </CardTitle>
                                <CardDescription className="line-clamp-2 text-xs text-muted-foreground/80 h-8 max-w-[90%]">
                                    {description || activePersona.description}
                                </CardDescription>
                            </div>
                        </div>

                        <div className="flex items-center gap-4" onClick={(e) => e.stopPropagation()}>
                            {/* Master Toggle? Or Contextual Toggle? Let's do Contextual for precision */}
                            <div className="flex flex-col items-end gap-1">
                                <Switch
                                    key={activePersona.id}
                                    checked={isContextActive}
                                    onCheckedChange={(val) => {
                                        // If forced mode, we might need to update timeframe first
                                        if (forcedTimeframe && forcedTimeframe.toLowerCase() !== timeframes[0]?.toLowerCase()) {
                                            // Pass the new timeframe to the handler
                                            onToggle(activePersona.id, val, forcedTimeframe)
                                        } else {
                                            onToggle(activePersona.id, val)
                                        }
                                    }}
                                    disabled={isToggling}
                                    className="data-[state=checked]:bg-primary"
                                />
                                <span className="text-[10px] text-muted-foreground">
                                    {isContextActive ? 'Active' : 'Paused'}
                                </span>
                            </div>
                        </div>
                    </div>
                </CardHeader>

                <CardContent className="space-y-5">
                    {/* Token Selector (Tabs style) */}
                    <div className="flex flex-wrap gap-2" onClick={(e) => e.stopPropagation()}>
                        {sortedPersonas.map(p => {
                            const token = p.symbol || ((p.tokens && p.tokens[0]) ? p.tokens[0] : 'RAW')
                            const isSelected = p.id === activePersonaId

                            // Contextual Active for specific token
                            const pTf = p.timeframes?.[0] || '4h'
                            const pIsContextActive = p.isActive && (!forcedTimeframe || (pTf.toLowerCase() === forcedTimeframe.toLowerCase()))

                            // "Illuminated" logic: If active, show full color. If paused, show muted.
                            // Selection is indicated by a separate ring/border interaction.
                            const baseColor = pIsContextActive
                                ? getTokenColor(token)
                                : "border-border bg-secondary/30 text-muted-foreground hover:bg-secondary hover:text-foreground"

                            return (
                                <button
                                    key={p.id}
                                    onClick={() => setActivePersonaId(p.id)}
                                    className={cn(
                                        "flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition-all relative",
                                        baseColor,
                                        // High contrast ring for selection
                                        isSelected && "ring-2 ring-primary ring-offset-2 ring-offset-card"
                                    )}
                                >
                                    {/* Optional Dot for Status - REMOVED for clarity (User Request) */}
                                    {/* <div className={cn("w-1.5 h-1.5 rounded-full", p.isActive ? "bg-success" : "bg-muted-foreground/30")} /> */}
                                    {token}
                                </button>
                            )
                        })}
                    </div>

                    {/* Context-Aware Stats */}
                    <div className="grid grid-cols-3 gap-2 py-3 bg-secondary/20 rounded-lg border border-border/50 px-3 transition-opacity duration-300">
                        <div className="space-y-0.5">
                            <span className="text-[10px] uppercase text-muted-foreground font-medium">Win Rate</span>
                            <div className={cn("text-lg font-bold tabular-nums", hasData ? "text-success" : "text-muted-foreground/50")}>
                                {winRateDisplay}
                            </div>
                        </div>
                        <div className="space-y-0.5">
                            <span className="text-[10px] uppercase text-muted-foreground font-medium">ROI (Est)</span>
                            <div className={cn("text-lg font-bold tabular-nums", hasData ? "text-foreground" : "text-muted-foreground/50")}>
                                {activePersona.expectedRoi || '--'}
                            </div>
                        </div>
                        <div className="space-y-0.5">
                            <span className="text-[10px] uppercase text-muted-foreground font-medium">Signals</span>
                            <div className={cn("text-lg font-bold tabular-nums", hasData ? "text-foreground" : "text-muted-foreground/50")}>
                                {activePersona.signals || 0}
                            </div>
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="flex items-center justify-between text-[11px] text-muted-foreground pt-1">
                        <div className="flex items-center gap-2">
                            {/* Timeframe Selector */}
                            {/* Timeframe Selector - Hidden if forcedTimeframe is active */}
                            {!forcedTimeframe && (
                                <div className="flex bg-secondary/30 rounded-md p-0.5 border border-border/50 relative">
                                    {['1h', '4h', '1d'].map((tf) => {
                                        const isPro = tf === '1h';
                                        const locked = isPro && !canAccessTimeframe('1H');
                                        // Current config in DB
                                        const currentTf = activePersona.timeframes?.[0] || '4h'
                                        const isActiveConfig = currentTf.toLowerCase() === tf.toLowerCase()

                                        // Visual Logic:
                                        // If Strategy is RUNNING (isActive), the active config should be highlighted prominently (Primary Color).
                                        // If Strategy is PAUSED, the active config is just selected (Secondary/Muted).
                                        // Other buttons are allowed to be clicked to CHANGE the config.

                                        return (
                                            <button
                                                key={tf}
                                                disabled={locked}
                                                onClick={async (e) => {
                                                    e.stopPropagation()
                                                    e.preventDefault()

                                                    if (isActiveConfig || locked) return

                                                    try {
                                                        const promise = strategiesService.updatePersona(activePersona.id, { timeframe: tf })
                                                        toast.promise(promise, {
                                                            loading: 'Updating timeframe...',
                                                            success: `Timeframe set to ${tf.toUpperCase()}`,
                                                            error: 'Failed to update'
                                                        })

                                                        await promise;

                                                        if (onRefresh) {
                                                            await onRefresh()
                                                        } else {
                                                            window.location.reload()
                                                        }
                                                    } catch (err) {
                                                        console.error(err)
                                                    }
                                                }}
                                                className={cn(
                                                    "px-2 py-0.5 rounded text-[10px] font-medium transition-all flex items-center gap-1 z-10 relative cursor-pointer min-w-[32px] justify-center",
                                                    isActiveConfig
                                                        ? (activePersona.isActive ? "bg-primary text-primary-foreground shadow-md font-bold" : "bg-foreground/10 text-foreground font-semibold")
                                                        : "text-muted-foreground hover:text-foreground/80 hover:bg-secondary/50",
                                                    locked && "opacity-50 cursor-not-allowed"
                                                )}
                                            >
                                                {locked && <Lock className="h-2 w-2" />}
                                                {tf.toUpperCase()}
                                            </button>
                                        )
                                    })}
                                </div>
                            )}

                            <span className="flex items-center gap-1 ml-1">
                                <TrendingUp className="h-3 w-3 opacity-70" />
                                {activePersona.riskLevel || 'Medium'} Risk
                            </span>
                        </div>

                        {!hasData ? (
                            <span className="text-xs italic opacity-50">Calibrating...</span>
                        ) : (
                            <button onClick={() => setShowDetails(true)} className="text-xs text-primary hover:underline">
                                View History
                            </button>
                        )}
                    </div>

                </CardContent>

                {/* Access Overlay */}
                {!hasAccess && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/80 backdrop-blur-sm z-20">
                        <Lock className="h-8 w-8 text-muted-foreground mb-2" />
                        <p className="text-sm font-medium text-muted-foreground">PRO Strategy</p>
                        <Link href="/pricing" onClick={(e) => e.stopPropagation()}>
                            <Badge variant="outline" className="mt-2 border-primary/30 text-primary text-xs cursor-pointer hover:bg-primary/10">
                                Upgrade to PRO
                            </Badge>
                        </Link>
                    </div>
                )}
            </Card>
            <StrategyDetailsSheet
                strategy={activePersona}
                isOpen={showDetails}
                onClose={() => setShowDetails(false)}
            />
        </>
    )
}
