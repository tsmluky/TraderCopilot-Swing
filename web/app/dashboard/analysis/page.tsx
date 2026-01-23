'use client'

import { useState } from 'react'
import { Search, Zap, Lock, BarChart2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { toast } from 'sonner'
import { analysisService } from '@/services/analysis'
import { useAuth } from '@/context/auth-context'
import { TOKEN_INFO } from '@/lib/types'
import type { Token, Timeframe } from '@/lib/types'

export default function AnalysisPage() {
    const { entitlements, allowedTokens, canAccessTimeframe } = useAuth()

    // State
    const [selectedToken, setSelectedToken] = useState<Token>('BTC')
    const [selectedTimeframe, setSelectedTimeframe] = useState<Timeframe>('4H')
    const [mode, setMode] = useState<'LITE' | 'PRO'>('LITE')
    const [isLoading, setIsLoading] = useState(false)
    const [result, setResult] = useState<any>(null)

    // Entitlement Checks
    const hasProAccess = entitlements?.tier === 'PRO' || entitlements?.plan_label === 'SwingPro' // or check feature flag
    const isTimeframeLocked = !canAccessTimeframe(selectedTimeframe)
    // If timeframe is locked, we might force user to upgrade or just show lock.

    const handleAnalyze = async () => {
        if (!allowedTokens.includes(selectedToken)) {
            toast.error(`You do not have access to analyze ${selectedToken}`)
            return
        }
        if (isTimeframeLocked) {
            toast.error(`Upgrade to PRO to analyze on ${selectedTimeframe} timeframe`)
            return
        }

        setIsLoading(true)
        setResult(null)

        try {
            let data;
            if (mode === 'PRO') {
                if (!hasProAccess) {
                    toast.error("Pro Analysis requires SwingPro plan")
                    setIsLoading(false)
                    return
                }
                data = await analysisService.analyzePro({
                    token: selectedToken,
                    timeframe: selectedTimeframe
                })
            } else {
                data = await analysisService.analyzeLite({
                    token: selectedToken,
                    timeframe: selectedTimeframe
                })
            }
            setResult(data)
        } catch (e: any) {
            toast.error(e.message || "Analysis failed")
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="space-y-6 max-w-5xl mx-auto">
            <div className="flex flex-col gap-4">
                <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
                    <BarChart2 className="w-6 h-6 text-primary" />
                    Market Analyzer
                </h1>
                <p className="text-muted-foreground">
                    Generate AI-powered technical analysis on demand.
                </p>
            </div>

            <div className="grid gap-6 md:grid-cols-[300px_1fr]">
                {/* Controls */}
                <div className="space-y-6">
                    <Card className="bg-card border-border">
                        <CardHeader>
                            <CardTitle className="text-sm font-medium uppercase tracking-wide text-muted-foreground">Configuration</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Token</label>
                                <Select value={selectedToken} onValueChange={(v: Token) => setSelectedToken(v)}>
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {Object.keys(TOKEN_INFO).map((t) => (
                                            <SelectItem key={t} value={t} disabled={!allowedTokens.includes(t)}>
                                                {t} {(!allowedTokens.includes(t)) && '(Locked)'}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">Timeframe</label>
                                <Select value={selectedTimeframe} onValueChange={(v: Timeframe) => setSelectedTimeframe(v)}>
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {['1H', '4H', '1D'].map((tf) => (
                                            <SelectItem key={tf} value={tf} disabled={!canAccessTimeframe(tf) && mode === 'PRO'}>
                                                {tf} {(!canAccessTimeframe(tf)) && '(Locked)'}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="space-y-2 pt-2 border-t border-border">
                                <label className="text-sm font-medium flex items-center justify-between">
                                    Analysis Mode
                                    {mode === 'PRO' && <Badge variant="secondary" className="text-xs bg-primary/10 text-primary">PRO</Badge>}
                                </label>
                                <div className="grid grid-cols-2 gap-2">
                                    <Button
                                        variant={mode === 'LITE' ? 'default' : 'outline'}
                                        onClick={() => setMode('LITE')}
                                        className="w-full"
                                    >
                                        Lite
                                    </Button>
                                    <Button
                                        variant={mode === 'PRO' ? 'default' : 'outline'}
                                        onClick={() => setMode('PRO')}
                                        className="w-full relative"
                                        disabled={!hasProAccess}
                                    >
                                        Pro
                                        {!hasProAccess && <Lock className="w-3 h-3 absolute top-1 right-1 text-muted-foreground" />}
                                    </Button>
                                </div>
                            </div>

                            <Button
                                className="w-full gap-2 mt-2"
                                size="lg"
                                onClick={handleAnalyze}
                                disabled={isLoading}
                            >
                                {isLoading ? <span className="animate-spin">⏳</span> : <Zap className="w-4 h-4 fill-current" />}
                                {isLoading ? 'Analyzing...' : 'Run Analysis'}
                            </Button>
                        </CardContent>
                    </Card>
                </div>

                {/* Results */}
                <div className="min-h-[400px]">
                    {result ? (
                        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <Card className="bg-card border-border border-primary/20 shadow-lg">
                                <CardHeader className="pb-2 border-b border-border/50">
                                    <div className="flex justify-between items-center">
                                        <div className="flex items-center gap-2">
                                            <Badge variant="outline" className="text-lg px-3 py-1 bg-background/50">{selectedToken}</Badge>
                                            <Badge variant="secondary">{selectedTimeframe}</Badge>
                                            <Badge className={mode === 'PRO' ? 'bg-primary' : 'bg-muted text-muted-foreground'}>{mode}</Badge>
                                        </div>
                                        <span className="text-xs text-muted-foreground">Generated just now</span>
                                    </div>
                                </CardHeader>
                                <CardContent className="p-6 prose prose-invert max-w-none prose-sm sm:prose-base">
                                    {/* Render different content based on structure. Assuming markdown or structured text */}
                                    <div className="whitespace-pre-wrap font-sans text-foreground/90 leading-relaxed">
                                        {result.analysis || result.content || JSON.stringify(result, null, 2)}
                                    </div>

                                    {result.signal && (
                                        <div className="mt-6 p-4 rounded-lg bg-secondary/30 border border-border">
                                            <h4 className="font-semibold mb-2 flex items-center gap-2">
                                                <Zap className="w-4 h-4 text-warning" />
                                                Signal Detected
                                            </h4>
                                            <div className="grid grid-cols-2 gap-4 text-sm">
                                                <div>Type: <span className="font-mono font-medium">{result.signal.type}</span></div>
                                                <div>Entry: <span className="font-mono">${result.signal.entry_price}</span></div>
                                                <div>Stop Loss: <span className="font-mono text-destructive">${result.signal.stop_loss}</span></div>
                                                <div>Target: <span className="font-mono text-success">${result.signal.target_price}</span></div>
                                            </div>
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-muted-foreground border-2 border-dashed border-border rounded-xl bg-card/10 p-12">
                            <BarChart2 className="w-16 h-16 mb-4 opacity-20" />
                            <p>Select a token and timeframe to start analysis.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
