import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Loader2, ScanLine, AlertTriangle, CheckCircle2, XCircle, Info, Lock } from 'lucide-react'
import { analysisService } from '@/services/analysis'
import { SignalCard } from '@/components/dashboard/signal-card'
import type { Signal } from '@/lib/types'
import { TOKEN_INFO } from '@/lib/types'
import { toast } from 'sonner'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { useUser } from '@/lib/user-context'
import { cn } from '@/lib/utils'

interface ScanDialogProps {
    onScanComplete?: () => void
}

export function ScanDialog({ onScanComplete }: ScanDialogProps) {
    const [isOpen, setIsOpen] = useState(false)
    const [token, setToken] = useState('BTC')
    const [timeframe, setTimeframe] = useState('4H')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<Signal | null>(null)
    const [mounted, setMounted] = useState(false)
    const { canAccessToken, canAccessTimeframe } = useUser()

    // Hydration fix
    useEffect(() => {
        setMounted(true)
    }, [])

    const handleScan = async () => {
        try {
            setLoading(true)
            setResult(null)

            const data = await analysisService.analyzeLite({
                token,
                timeframe,
                message: 'Manual Scan from Dashboard'
            })

            const newSignal: Signal = {
                id: data.id || 'temp-id',
                token: data.token,
                type: data.direction.toUpperCase(), // LONG/SHORT/NEUTRAL
                entryPrice: data.entry,
                targetPrice: data.tp,
                stopLoss: data.sl,
                timeframe: data.timeframe,
                timestamp: data.timestamp,
                status: 'ACTIVE', // Assumed active
                confidence: (data.confidence * 100),
                evaluation: 'pending',
                rationale: data.rationale,
                indicators: data.indicators,
                watchlist: data.watchlist
            }

            if (data.confidence <= 1.0) {
                newSignal.confidence = data.confidence * 100
            } else {
                newSignal.confidence = data.confidence
            }

            setResult(newSignal)
            toast.success(`Scan Complete: ${data.direction.toUpperCase()}`)

            if (onScanComplete) onScanComplete()

        } catch (e) {
            console.error(e)
            toast.error("Scan failed. Please try again.")
        } finally {
            setLoading(false)
        }
    }

    const reset = () => {
        setResult(null)
        setLoading(false)
    }

    if (!mounted) {
        return (
            <Button className="gap-2 shadow-lg shadow-primary/20">
                <ScanLine className="h-4 w-4" />
                Scan Opportunity
            </Button>
        )
    }

    const STRATEGY_DISPLAY = {
        'donchian_v2': { name: 'Titan Breakout', color: 'text-indigo-500' },
        'trend_following_native_v1': { name: 'Flow Master', color: 'text-emerald-500' },
        'lite_swing_confluence': { name: 'Confluence', color: 'text-amber-500' }
    } as const

    const getStrategyName = (id: string) => {
        // @ts-ignore
        const config = STRATEGY_DISPLAY[id]
        if (config) return config.name
        return id.replace(/_/g, ' ').toUpperCase()
    }

    const SUPPORTED_TOKENS = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP']

    return (
        <Dialog open={isOpen} onOpenChange={(v) => { setIsOpen(v); if (!v) reset(); }}>
            <DialogTrigger asChild>
                <Button className="gap-2 shadow-lg shadow-primary/20 bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-300">
                    <ScanLine className="h-4 w-4" />
                    Scan Opportunity
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px] border-black/5 dark:border-white/10 bg-white dark:bg-card shadow-2xl p-0 gap-0 overflow-hidden">

                {/* Header */}
                <DialogHeader className="p-5 border-b border-black/5 dark:border-white/5 bg-black/[0.02] dark:bg-white/[0.02]">
                    <div className="flex items-center gap-3">
                        <div className="bg-primary/10 p-2 rounded-xl border border-primary/10 shadow-inner">
                            <ScanLine className="h-5 w-5 text-primary" />
                        </div>
                        <div className="space-y-0.5">
                            <DialogTitle className="flex items-center gap-2 text-xl">
                                Market Scanner
                                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10 text-muted-foreground uppercase tracking-wider">
                                    LITE
                                </span>
                            </DialogTitle>
                            <DialogDescription className="text-xs">
                                Real-time algorithmic analysis across <strong>{Object.keys(STRATEGY_DISPLAY).length}</strong> strategies.
                            </DialogDescription>
                        </div>
                    </div>
                </DialogHeader>

                {!result ? (
                    <div className="p-6 grid gap-6">

                        {/* Token Selector */}
                        <div className="space-y-3">
                            <Label className="text-sm font-medium text-foreground ml-1">Asset Selection</Label>
                            <div className="flex items-center gap-2 flex-wrap">
                                {Object.keys(TOKEN_INFO).map((t) => {
                                    const isAllowed = canAccessToken(t as any)
                                    const isActive = token === t

                                    // Helper for colors
                                    const getColor = (tok: string, active: boolean) => {
                                        if (!active) return "hover:border-primary/30 hover:bg-primary/5 text-muted-foreground hover:text-foreground"
                                        switch (tok) {
                                            case 'BTC': return "bg-orange-500/10 border-orange-500 text-orange-600 dark:text-orange-400 shadow-[0_0_10px_rgba(249,115,22,0.15)] font-bold"
                                            case 'ETH': return "bg-indigo-500/10 border-indigo-500 text-indigo-600 dark:text-indigo-400 shadow-[0_0_10px_rgba(99,102,241,0.15)] font-bold"
                                            case 'SOL': return "bg-teal-500/10 border-teal-500 text-teal-600 dark:text-teal-400 shadow-[0_0_10px_rgba(20,184,166,0.15)] font-bold"
                                            case 'BNB': return "bg-yellow-500/10 border-yellow-500 text-yellow-600 dark:text-yellow-400 shadow-[0_0_10px_rgba(234,179,8,0.15)] font-bold"
                                            case 'XRP': return "bg-blue-500/10 border-blue-500 text-blue-600 dark:text-blue-400 shadow-[0_0_10px_rgba(59,130,246,0.15)] font-bold"
                                            default: return "bg-primary text-primary-foreground font-bold"
                                        }
                                    }

                                    return (
                                        <button
                                            key={t}
                                            disabled={!isAllowed}
                                            onClick={() => setToken(t)}
                                            className={cn(
                                                "flex-1 h-10 min-w-[3rem] text-sm rounded-lg border transition-all duration-200 flex items-center justify-center relative",
                                                !isAllowed ? "opacity-50 cursor-not-allowed bg-secondary/50 border-transparent" : "bg-white dark:bg-secondary/30 border-black/5 dark:border-white/5",
                                                getColor(t, isActive),
                                                isActive && "translate-y-[-1px]"
                                            )}
                                        >
                                            {t}
                                            {!isAllowed && <Lock className="absolute top-1 right-1 h-2 w-2 opacity-50" />}
                                        </button>
                                    )
                                })}
                            </div>
                        </div>

                        {/* Timeframe Selector */}
                        <div className="space-y-3">
                            <Label className="text-sm font-medium text-foreground ml-1">Timeframe</Label>
                            <div className="flex items-center gap-2">
                                {['1H', '4H', '1D'].map((tf) => {
                                    const isAllowed = canAccessTimeframe(tf as any)
                                    const isActive = timeframe === tf
                                    return (
                                        <button
                                            key={tf}
                                            disabled={!isAllowed}
                                            onClick={() => setTimeframe(tf)}
                                            className={cn(
                                                "flex-1 h-10 rounded-lg border text-sm font-medium transition-all duration-200 flex items-center justify-center relative",
                                                !isAllowed ? "opacity-50 cursor-not-allowed bg-secondary/50 border-transparent text-muted-foreground" :
                                                    isActive
                                                        ? "bg-primary text-primary-foreground shadow-md shadow-primary/20 border-primary"
                                                        : "bg-white dark:bg-secondary/30 border-black/5 dark:border-white/5 text-muted-foreground hover:text-foreground hover:bg-black/5 dark:hover:bg-white/5"
                                            )}
                                        >
                                            {tf}
                                            {!isAllowed && <Lock className="absolute top-1 right-1 h-2 w-2 opacity-50" />}
                                        </button>
                                    )
                                })}
                            </div>
                        </div>

                        <div className="pt-2 space-y-3">
                            <Button
                                onClick={handleScan}
                                disabled={loading}
                                className="w-full h-12 text-sm font-bold shadow-lg shadow-primary/20 rounded-xl transition-all hover:scale-[1.01] active:scale-[0.99] bg-primary text-primary-foreground hover:bg-primary/90"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Scanning Market...
                                    </>
                                ) : (
                                    'Start Algorithmic Scan'
                                )}
                            </Button>

                            <div className="flex items-center justify-center gap-1.5 text-[10px] text-muted-foreground opacity-60">
                                <ScanLine className="h-3 w-3" />
                                <span className="uppercase tracking-widest font-mono">SwingEngine™ v1.0 Active</span>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col h-full min-h-[400px]">
                        {result.type === 'NEUTRAL' ? (
                            <div className="flex-1 flex flex-col p-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                                {result.watchlist && result.watchlist.length > 0 ? (
                                    <div className="flex-1 flex flex-col space-y-4">
                                        <div className="bg-gradient-to-br from-secondary/50 via-background to-secondary/30 rounded-xl p-4 border border-border/50">
                                            <div className="flex items-center gap-3 mb-4">
                                                <div className="h-9 w-9 rounded-full bg-primary/10 flex items-center justify-center shadow-inner">
                                                    <ScanLine className="h-4.5 w-4.5 text-primary" />
                                                </div>
                                                <div>
                                                    <h3 className="font-bold text-sm text-foreground">Opportunities Detected</h3>
                                                    <p className="text-xs text-muted-foreground">High potential setups forming soon.</p>
                                                </div>
                                            </div>

                                            <div className="space-y-3">
                                                {result.watchlist.map((item, idx) => (
                                                    <div key={idx} className="bg-white dark:bg-card hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors rounded-lg p-3 border border-black/5 dark:border-white/5 shadow-sm group">
                                                        <div className="flex justify-between items-start mb-2">
                                                            <div className="flex items-center gap-2">
                                                                <span className={cn(
                                                                    "px-1.5 py-0.5 rounded text-[10px] font-black uppercase tracking-wider border",
                                                                    item.side === 'long'
                                                                        ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
                                                                        : "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20"
                                                                )}>
                                                                    {item.side}
                                                                </span>
                                                                <span className="font-bold text-xs text-foreground/90">{getStrategyName(item.strategy_id)}</span>
                                                            </div>
                                                            <div className="text-[10px] font-mono font-medium text-muted-foreground bg-secondary/50 px-1.5 py-0.5 rounded">
                                                                {item.distance_atr.toFixed(2)} ATR
                                                            </div>
                                                        </div>

                                                        <div className="text-xs text-muted-foreground mb-3 leading-relaxed border-l-2 border-primary/20 pl-2">
                                                            {item.reason}
                                                        </div>

                                                        <Button
                                                            variant="default"
                                                            size="sm"
                                                            className="w-full h-8 text-xs font-medium bg-primary/5 text-primary hover:bg-primary/10 hover:text-primary border border-primary/10 shadow-none transition-all"
                                                            onClick={async () => {
                                                                try {
                                                                    const tid = toast.loading("Configuring Watch...")
                                                                    const { apiFetch } = await import('@/lib/api-client')
                                                                    const res = await apiFetch<{ status: string; expires_at: string }>('/api/alerts/watch', {
                                                                        method: 'POST',
                                                                        body: JSON.stringify({
                                                                            token: result.token,
                                                                            timeframe: result.timeframe,
                                                                            strategy_id: item.strategy_id,
                                                                            side: item.side,
                                                                            trigger_price: item.trigger_price,
                                                                            distance_atr: item.distance_atr,
                                                                            reason: item.reason
                                                                        })
                                                                    })
                                                                    toast.dismiss(tid)
                                                                    toast.success("Added to Watchlist", {
                                                                        description: `Alert active until ${new Date(res.expires_at).toLocaleTimeString()}`
                                                                    })
                                                                } catch (e) {
                                                                    console.error(e)
                                                                    toast.error("Failed to add watch")
                                                                }
                                                            }}
                                                        >
                                                            <ScanLine className="h-3 w-3 mr-1.5" /> Watch (Notify me on Telegram)
                                                        </Button>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                        <Button variant="outline" onClick={reset} className="w-full h-10 border-black/5 dark:border-white/5 hover:bg-black/5 dark:hover:bg-white/5">
                                            Scan Another Asset
                                        </Button>
                                    </div>
                                ) : (
                                    <div className="flex flex-col items-center justify-center flex-1 py-10 text-center space-y-4">
                                        <div className="h-14 w-14 rounded-full bg-secondary/30 flex items-center justify-center mb-2 animate-pulse">
                                            <div className="relative">
                                                <ScanLine className="h-7 w-7 text-muted-foreground/50" />
                                            </div>
                                        </div>
                                        <div className="space-y-2">
                                            <h3 className="font-bold text-lg">No Actionable Setup</h3>
                                            <p className="text-sm text-muted-foreground max-w-[280px] mx-auto leading-relaxed">
                                                Market conditions for <strong>{token}</strong> ({timeframe}) don't match our high-probability criteria right now.
                                            </p>
                                        </div>
                                        <div className="pt-4 w-full max-w-xs">
                                            <Button variant="outline" onClick={reset} className="w-full h-11 border-dashed shadow-sm">
                                                Try Different Pair
                                            </Button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="flex-1 flex flex-col p-6 animate-in fade-in slide-in-from-bottom-2 duration-300 space-y-6">
                                <div className="text-center space-y-2">
                                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 text-xs font-bold uppercase tracking-wider mb-2">
                                        <CheckCircle2 className="h-3.5 w-3.5" />
                                        Valid Setup Found
                                    </div>
                                    <h3 className="text-2xl font-black">{result.token} {result.type}</h3>
                                </div>

                                <div className="border border-emerald-500/20 shadow-xl shadow-emerald-500/5 bg-white dark:bg-card rounded-xl overflow-hidden">
                                    <SignalCard signal={result} compact />
                                </div>

                                <div className="rounded-xl p-4 border border-emerald-500/20 bg-emerald-500/5">
                                    <div className="flex items-start gap-3">
                                        <div className="h-8 w-8 rounded-full bg-emerald-500/10 flex items-center justify-center shrink-0">
                                            <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                                        </div>
                                        <div>
                                            <h4 className="font-bold text-sm text-emerald-700 dark:text-emerald-400">Algorithmic Validation</h4>
                                            <p className="text-xs text-muted-foreground/80 mt-1 leading-relaxed">
                                                Confirmed high-probability setup based on <strong>{getStrategyName(result.indicators?.strategy_id || 'Unknown')}</strong> logic.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                <Button className="w-full h-12 bg-emerald-600 hover:bg-emerald-700 text-white font-bold shadow-lg shadow-emerald-600/20" onClick={() => setIsOpen(false)}>
                                    View Full Signal Analysis
                                </Button>
                            </div>
                        )}

                        {/* Diagnostics Toggle - Only show if we have diagnostics and it's not a generic 'No Setup' without hints */}
                        {(result.indicators?.strategies || (result.type === 'NEUTRAL' && result.watchlist?.length === 0)) && (
                            <div className="p-3 bg-secondary/5 border-t border-black/5 dark:border-white/5">
                                <Accordion type="single" collapsible className="w-full">
                                    <AccordionItem value="details" className="border-0">
                                        <AccordionTrigger className="text-[10px] text-muted-foreground py-1 justify-center hover:no-underline hover:text-foreground group min-h-0 h-6">
                                            <div className="flex items-center gap-1.5 opacity-70 group-hover:opacity-100 transition-opacity">
                                                <Info className="h-3 w-3" />
                                                View Strategy Diagnostics
                                            </div>
                                        </AccordionTrigger>
                                        <AccordionContent>
                                            <div className="space-y-2 mt-3 mb-1">
                                                {result.indicators?.strategies?.map((strat: any, i: number) => (
                                                    <div key={i} className="flex flex-col gap-2 p-3 bg-white dark:bg-card rounded-lg border border-black/5 dark:border-white/5 shadow-sm">
                                                        <div className="flex items-center justify-between">
                                                            <span className="font-bold text-xs text-foreground/80">
                                                                {getStrategyName(strat.strategy_id)}
                                                            </span>
                                                            {strat.has_setup ? (
                                                                <span className="text-emerald-600 dark:text-emerald-400 text-[10px] font-bold flex items-center gap-1">
                                                                    <CheckCircle2 className="h-3 w-3" /> MATCH
                                                                </span>
                                                            ) : (
                                                                <span className="text-muted-foreground text-[10px] font-bold flex items-center gap-1 opacity-70">
                                                                    <XCircle className="h-3 w-3" /> NO MATCH
                                                                </span>
                                                            )}
                                                        </div>

                                                        {strat.state && !strat.state.status && (
                                                            <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-[10px] font-mono text-muted-foreground/70 border-t border-dashed border-border/50 pt-2 mt-1">
                                                                {/* Example logic for displaying internal indicators */}
                                                                {strat.strategy_id.includes('trend') && strat.state.indicators && (
                                                                    <>
                                                                        <span>EMA(20): <span className="text-foreground">{strat.state.indicators.ema_fast?.toFixed(2)}</span></span>
                                                                        <span>EMA(50): <span className="text-foreground">{strat.state.indicators.ema_slow?.toFixed(2)}</span></span>
                                                                        <span className="col-span-2 mt-0.5">
                                                                            Trend: <span className={strat.state.state?.trend === 'Bullish' ? 'text-emerald-500' : 'text-red-500'}>{strat.state.state?.trend}</span>
                                                                        </span>
                                                                    </>
                                                                )}
                                                            </div>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        </AccordionContent>
                                    </AccordionItem>
                                </Accordion>
                            </div>
                        )}
                    </div>
                )}
            </DialogContent>
        </Dialog>
    )
}
