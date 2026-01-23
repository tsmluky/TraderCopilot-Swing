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

    return (
        <Dialog open={isOpen} onOpenChange={(v) => { setIsOpen(v); if (!v) reset(); }}>
            <DialogTrigger asChild>
                <Button className="gap-2 shadow-lg shadow-primary/20">
                    <ScanLine className="h-4 w-4" />
                    Scan Opportunity
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Scan Market (LITE)</DialogTitle>
                    <DialogDescription>
                        Check for Swing setups using active strategies.
                    </DialogDescription>
                </DialogHeader>

                {!result ? (
                    <div className="grid gap-4 py-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Token</Label>
                                <Select value={token} onValueChange={setToken}>
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {Object.keys(TOKEN_INFO).map(t => {
                                            const isAllowed = canAccessToken(t as any) // Assuming allowedTokens.includes(t)
                                            return (
                                                <SelectItem key={t} value={t} disabled={!isAllowed} className="flex items-center justify-between w-full">
                                                    <div className="flex items-center gap-2 w-full justify-between">
                                                        <span>{t}</span>
                                                        {!isAllowed && <Lock className="h-3 w-3 opacity-50" />}
                                                    </div>
                                                </SelectItem>
                                            )
                                        })}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-2">
                                <Label>Timeframe</Label>
                                <Select value={timeframe} onValueChange={setTimeframe}>
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {['1H', '4H', '1D'].map(tf => {
                                            const isAllowed = canAccessTimeframe(tf as any)
                                            return (
                                                <SelectItem key={tf} value={tf} disabled={!isAllowed} className="flex items-center justify-between w-full">
                                                    <div className="flex items-center gap-2 w-full justify-between">
                                                        <span>{tf}</span>
                                                        {!isAllowed && <Lock className="h-3 w-3 opacity-50" />}
                                                    </div>
                                                </SelectItem>
                                            )
                                        })}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        <Button onClick={handleScan} disabled={loading} className="w-full mt-2">
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Scanning Strategies...
                                </>
                            ) : (
                                'Run Analysis'
                            )}
                        </Button>

                        <p className="text-xs text-muted-foreground text-center">
                            Uses Donchian & TrendFollowing strategies.
                        </p>
                    </div>
                ) : (
                    <div className="py-2 space-y-4">
                        {result.type === 'NEUTRAL' ? (
                            <div className="space-y-4">
                                {result.watchlist && result.watchlist.length > 0 ? (
                                    <div className="space-y-4">
                                        <div className="bg-secondary/10 rounded-lg p-4 border border-border/50">
                                            <div className="flex items-center gap-2 mb-3">
                                                <Info className="h-4 w-4 text-primary" />
                                                <h3 className="font-semibold text-sm">No confirmed setup, but found opportunities:</h3>
                                            </div>

                                            <div className="space-y-3">
                                                {result.watchlist.map((item, idx) => (
                                                    <div key={idx} className="bg-card rounded-md p-3 border border-border/40 text-sm shadow-sm relative group">
                                                        <div className="flex justify-between items-start mb-2">
                                                            <div className="flex items-center gap-2">
                                                                <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${item.side === 'long' ? 'bg-success/20 text-success' : 'bg-destructive/20 text-destructive'}`}>
                                                                    {item.side}
                                                                </span>
                                                                <span className="font-medium text-xs text-muted-foreground uppercase">{item.strategy_id.replace('native_v1', '').replace('_v2', '').replace('_', ' ')}</span>
                                                            </div>
                                                            <div className="text-xs font-mono text-muted-foreground">
                                                                {item.distance_atr.toFixed(2)} ATR
                                                            </div>
                                                        </div>

                                                        <div className="text-xs text-foreground/90 mb-1.5 font-medium leading-relaxed">
                                                            {item.reason}
                                                        </div>

                                                        <div className="flex justify-between items-center text-[10px] text-muted-foreground border-t border-border/30 pt-2 mt-2">
                                                            <span>Trigger: <span className="text-foreground font-mono">${item.trigger_price.toFixed(2)}</span></span>
                                                            {item.missing && item.missing.length > 0 && (
                                                                <span className="italic opacity-80">{item.missing[0]}</span>
                                                            )}
                                                        </div>

                                                        {/* Action Buttons */}
                                                        <div className="mt-3 flex items-center gap-2 pt-2 border-t border-dashed border-border/40">
                                                            <Button
                                                                variant="default"
                                                                size="sm"
                                                                className="h-7 text-xs w-full bg-primary/10 text-primary hover:bg-primary/20 hover:text-primary transition-colors"
                                                                onClick={async () => {
                                                                    try {
                                                                        const tid = toast.loading("Creating Alert...")
                                                                        // api-client call
                                                                        const { apiFetch } = await import('@/lib/api-client')
                                                                        const res = await apiFetch<{ status: string; expires_at: string }>('/api/alerts/watch', {
                                                                            method: 'POST',
                                                                            body: JSON.stringify({
                                                                                token: result.token,
                                                                                timeframe: result.timeframe, // Use scan timeframe
                                                                                strategy_id: item.strategy_id,
                                                                                side: item.side,
                                                                                trigger_price: item.trigger_price,
                                                                                distance_atr: item.distance_atr,
                                                                                reason: item.reason
                                                                            })
                                                                        })
                                                                        toast.dismiss(tid)
                                                                        toast.success(`Alert Created! Expires: ${new Date(res.expires_at).toLocaleTimeString()}`)
                                                                    } catch (e) {
                                                                        console.error(e)
                                                                        toast.error("Failed to create alert")
                                                                    }
                                                                }}
                                                            >
                                                                <ScanLine className="h-3 w-3 mr-1.5" /> Set Alert (Telegram)
                                                            </Button>

                                                            <Button
                                                                variant="ghost"
                                                                size="sm"
                                                                className="h-7 text-xs w-full text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                                                                onClick={() => {
                                                                    toast('Early Entry Mode', {
                                                                        description: "High Risk: No confirmation yet. Manage your risk manually.",
                                                                        duration: 5000,
                                                                    })
                                                                }}
                                                            >
                                                                <AlertTriangle className="h-3 w-3 mr-1.5" /> Early Entry
                                                            </Button>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                        <p className="text-xs text-muted-foreground text-center px-4">
                                            These are near-miss setups. Monitor closely or wait for confirmation.
                                        </p>
                                        <Button variant="outline" size="sm" onClick={reset} className="w-full">
                                            Scan Another
                                        </Button>
                                    </div>
                                ) : (
                                    <div className="flex flex-col items-center justify-center p-6 border border-dashed rounded-lg bg-secondary/20 text-center">
                                        <AlertTriangle className="h-8 w-8 text-muted-foreground mb-2" />
                                        <h3 className="font-semibold">No Setup Detected</h3>
                                        <p className="text-sm text-muted-foreground mt-1 max-w-[280px]">
                                            {result.rationale || "Strategies returned no valid setup for this timeframe."}
                                        </p>
                                        <Button variant="outline" size="sm" onClick={reset} className="mt-4">
                                            Scan Another
                                        </Button>
                                    </div>
                                )}

                                {result.indicators?.strategies && (
                                    <Accordion type="single" collapsible className="w-full">
                                        <AccordionItem value="details" className="border-0">
                                            <AccordionTrigger className="text-xs text-muted-foreground py-2 justify-center hover:no-underline hover:text-foreground">
                                                <div className="flex items-center gap-1.5">
                                                    <Info className="h-3 w-3" />
                                                    View Technical Details
                                                </div>
                                            </AccordionTrigger>
                                            <AccordionContent>
                                                <div className="rounded-lg border border-border/50 bg-card p-3 space-y-3 mt-1">
                                                    <div className="text-xs font-medium text-muted-foreground mb-2">Strategy Status:</div>
                                                    {result.indicators.strategies.map((strat: any, i: number) => (
                                                        <div key={i} className="flex flex-col gap-1.5 p-2.5 bg-secondary/10 rounded-md border border-border/40">
                                                            <div className="flex items-center justify-between text-xs">
                                                                <span className="font-semibold text-foreground/90 font-mono tracking-tight">
                                                                    {strat.strategy_id.replace('native_v1', '').replace('_v2', '').toUpperCase().replace('_', ' ')}
                                                                </span>
                                                                {strat.has_setup ? (
                                                                    <span className="text-success flex items-center gap-1 bg-success/10 px-1.5 py-0.5 rounded text-[10px] font-medium">
                                                                        <CheckCircle2 className="h-3 w-3" /> SETUP
                                                                    </span>
                                                                ) : (
                                                                    <span className="text-muted-foreground flex items-center gap-1 bg-secondary/50 px-1.5 py-0.5 rounded text-[10px] font-medium">
                                                                        <XCircle className="h-3 w-3" /> WAIT
                                                                    </span>
                                                                )}
                                                            </div>

                                                            {/* Render State Details */}
                                                            {strat.state && !strat.state.status && (
                                                                <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-[10px] text-muted-foreground/80 font-mono pl-1 border-l-2 border-primary/20">
                                                                    {/* Trend Following */}
                                                                    {strat.strategy_id.includes('trend') && strat.state.indicators && (
                                                                        <>
                                                                            <span>EMA F: <span className="text-foreground">{strat.state.indicators.ema_fast?.toFixed(2)}</span></span>
                                                                            <span>EMA S: <span className="text-foreground">{strat.state.indicators.ema_slow?.toFixed(2)}</span></span>
                                                                            <span>ADX: <span className="text-foreground">{strat.state.indicators.adx?.toFixed(1)}</span></span>
                                                                            <span className={strat.state.state?.trend === 'Bullish' ? 'text-success/80' : 'text-destructive/80'}>
                                                                                {strat.state.state?.trend}
                                                                            </span>
                                                                        </>
                                                                    )}

                                                                    {/* Donchian */}
                                                                    {strat.strategy_id.includes('donchian') && strat.state.indicators && (
                                                                        <>
                                                                            <span>High: <span className="text-foreground">{strat.state.indicators.upper?.toFixed(2)}</span></span>
                                                                            <span>Low: <span className="text-foreground">{strat.state.indicators.lower?.toFixed(2)}</span></span>
                                                                            <span className="col-span-2">
                                                                                Pos: <span className="text-foreground">{strat.state.state?.position}</span>
                                                                            </span>
                                                                        </>
                                                                    )}
                                                                </div>
                                                            )}

                                                            {/* Error State */}
                                                            {strat.state?.status && (
                                                                <div className="text-[10px] text-destructive bg-destructive/5 p-1 rounded">
                                                                    {strat.state.details}
                                                                </div>
                                                            )}
                                                        </div>
                                                    ))}
                                                    <div className="pt-2 border-t border-border/50 text-[10px] text-muted-foreground">
                                                        Price: ${result.indicators.price} | Decision: {result.indicators.decision}
                                                    </div>
                                                </div>
                                            </AccordionContent>
                                        </AccordionItem>
                                    </Accordion>
                                )}
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <SignalCard signal={result} compact />
                                <div className="flex bg-secondary/20 rounded-lg p-3 gap-2 border border-border/50">
                                    <CheckCircle2 className="h-4 w-4 text-success shrink-0 mt-0.5" />
                                    <div>
                                        <p className="text-sm font-medium">Setup Found!</p>
                                        <p className="text-xs text-muted-foreground mt-0.5">
                                            Signal has been added to your dashboard history.
                                        </p>
                                    </div>
                                </div>
                                <Button className="w-full" onClick={() => setIsOpen(false)}>
                                    Done
                                </Button>
                            </div>
                        )}
                    </div>
                )}
            </DialogContent>
        </Dialog>
    )
}
