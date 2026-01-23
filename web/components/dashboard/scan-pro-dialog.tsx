import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Loader2, ScrollText, CheckCircle2, AlertTriangle, XCircle, FileText, Download, Lock } from 'lucide-react'
import { analysisService } from '@/services/analysis'
import { AuthError } from '@/lib/api-client'
import { toast } from 'sonner'
import ReactMarkdown from 'react-markdown'
import { cn } from '@/lib/utils'
import { useUser } from '@/lib/user-context'
import Link from 'next/link'

interface ScanProDialogProps {
    onScanComplete?: () => void
}

const SUPPORTED_TOKENS = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP']

export function ScanProDialog({ onScanComplete }: ScanProDialogProps) {
    const [isOpen, setIsOpen] = useState(false)
    const [token, setToken] = useState('BTC')
    const [language, setLanguage] = useState('en')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<any | null>(null)

    const handleScan = async () => {
        try {
            setLoading(true)
            setResult(null)

            const data = await analysisService.analyzePro({
                token,
                timeframe: '4H',
                user_message: '',
                language
            })

            setResult(data)
            toast.success(`PRO Analysis Complete (${token})`)

            if (onScanComplete) onScanComplete()

        } catch (e) {
            if (e instanceof AuthError) return
            console.error(e)
            toast.error("Analysis failed. Ensure you have PRO access.")
        } finally {
            setLoading(false)
        }
    }

    const reset = () => {
        setResult(null)
        setLoading(false)
    }

    const downloadReport = () => {
        if (!result) return
        const blob = new Blob([result.raw], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `Institutional_Analysis_${token}_${new Date().toISOString().split('T')[0]}.md`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        toast.success("Report downloaded")
    }

    const { user } = useUser()
    const isPro = user?.plan === 'PRO'

    const [mounted, setMounted] = useState(false)
    useEffect(() => {
        setMounted(true)
    }, [])

    if (!mounted || !isPro) {
        return (
            <Link href="/pricing">
                <Button variant="outline" className="gap-2 shadow-sm border-dashed border-primary/30 text-muted-foreground hover:text-primary hover:border-primary">
                    <Lock className="h-4 w-4" />
                    Institutional Analysis (PRO)
                </Button>
            </Link>
        )
    }

    return (
        <Dialog open={isOpen} onOpenChange={(v) => { setIsOpen(v); if (!v) reset(); }}>
            <DialogTrigger asChild>
                <Button variant="secondary" className="gap-2 shadow-sm border border-primary/20 bg-primary/5 text-primary hover:bg-primary/10">
                    <ScrollText className="h-4 w-4" />
                    Institutional Analysis (PRO)
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[700px] max-h-[85vh] overflow-hidden flex flex-col">
                <DialogHeader>
                    <div className="flex items-center justify-between pr-8">
                        <div className="flex items-center gap-2">
                            <div className="bg-primary/10 p-1.5 rounded-md">
                                <FileText className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                                <DialogTitle>Institutional Analysis</DialogTitle>
                                <DialogDescription>
                                    Deep-dive quantitative & macro report (2-6 Weeks Horizon).
                                </DialogDescription>
                            </div>
                        </div>

                        {/* Language Toggle - Sleek & Premium */}
                        {!result && !loading && (
                            <div className="flex items-center gap-2 text-sm select-none bg-secondary/30 p-1 rounded-lg border border-border/40">
                                <button
                                    onClick={() => setLanguage('en')}
                                    className={cn(
                                        "px-2 py-0.5 rounded-md transition-all duration-300 font-medium text-xs",
                                        language === 'en'
                                            ? "bg-primary text-primary-foreground shadow-sm"
                                            : "text-muted-foreground hover:text-foreground"
                                    )}
                                >
                                    EN
                                </button>
                                <button
                                    onClick={() => setLanguage('es')}
                                    className={cn(
                                        "px-2 py-0.5 rounded-md transition-all duration-300 font-medium text-xs",
                                        language === 'es'
                                            ? "bg-primary text-primary-foreground shadow-sm"
                                            : "text-muted-foreground hover:text-foreground"
                                    )}
                                >
                                    ES
                                </button>
                            </div>
                        )}
                    </div>
                </DialogHeader>

                {!result ? (
                    <div className="grid gap-6 py-6 px-1">
                        {/* Token Selector - Horizontal Cards */}
                        <div className="space-y-3">
                            <Label className="text-sm font-medium text-muted-foreground ml-1">Select Asset (PRO Universe)</Label>
                            <div className="flex items-center gap-3">
                                {SUPPORTED_TOKENS.map((t) => (
                                    <button
                                        key={t}
                                        onClick={() => setToken(t)}
                                        className={cn(
                                            "flex-1 h-14 rounded-xl border flex items-center justify-center transition-all duration-200",
                                            token === t
                                                ? "bg-primary/10 border-primary shadow-[0_0_15px_rgba(var(--primary),0.15)] ring-1 ring-primary"
                                                : "bg-background border-border hover:border-primary/50 hover:bg-secondary/50 text-muted-foreground"
                                        )}
                                    >
                                        <span className={cn(
                                            "text-lg font-bold tracking-tight",
                                            token === t ? "text-primary" : "text-muted-foreground"
                                        )}>
                                            {t}
                                        </span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        <Button onClick={handleScan} disabled={loading} className="w-full mt-4 h-14 text-lg font-bold shadow-lg shadow-primary/20 rounded-xl transition-all hover:scale-[1.01] active:scale-[0.99]">
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                                    Analyzing Institutional Data...
                                </>
                            ) : (
                                'Generate Institutional Report'
                            )}
                        </Button>

                        <div className="p-4 bg-secondary/20 rounded-xl border border-border/50 text-xs text-muted-foreground space-y-2 mt-2">
                            <p className="font-semibold text-foreground flex items-center gap-2">
                                <FileText className="h-3 w-3 text-primary" />
                                Report Scope:
                            </p>
                            <ul className="grid grid-cols-2 gap-2 pl-2">
                                <li className="flex items-center gap-1.5"><CheckCircle2 className="h-3 w-3 text-primary/50" /> Strategy Thesis</li>
                                <li className="flex items-center gap-1.5"><CheckCircle2 className="h-3 w-3 text-primary/50" /> Macro Regime</li>
                                <li className="flex items-center gap-1.5"><CheckCircle2 className="h-3 w-3 text-primary/50" /> Market Structure</li>
                                <li className="flex items-center gap-1.5"><CheckCircle2 className="h-3 w-3 text-primary/50" /> Bull/Bear Scenarios</li>
                            </ul>
                        </div>
                    </div>
                ) : (
                    <div className="flex-1 overflow-hidden flex flex-col min-h-0">
                        {/* Header Metrics */}
                        <div className="flex items-center justify-between p-3 bg-secondary/10 border-b border-border/50 shrink-0">
                            <div className="flex items-center gap-3 text-sm">
                                <span className="font-bold text-lg">{token}</span>
                                <span className="text-muted-foreground">|</span>
                                <span className="text-muted-foreground">Horizon: {result.indicators?.horizon || "2-6 Weeks"}</span>
                            </div>

                            <div className="flex items-center gap-2">
                                {/* Setup Status Badge */}
                                {result.indicators?.setup_status && (
                                    <div className={cn(
                                        "px-2.5 py-1 rounded-full text-xs font-medium border flex items-center gap-1.5",
                                        result.indicators.setup_status.decision === 'confluence'
                                            ? "bg-success/10 text-success border-success/20"
                                            : result.indicators.setup_status.decision === 'neutral_no_setup'
                                                ? "bg-secondary text-muted-foreground border-border"
                                                : "bg-destructive/10 text-destructive border-destructive/20"
                                    )}>
                                        {result.indicators.setup_status.decision === 'confluence' ? <CheckCircle2 className="h-3 w-3" /> :
                                            result.indicators.setup_status.decision === 'neutral_no_setup' ? <AlertTriangle className="h-3 w-3" /> :
                                                <XCircle className="h-3 w-3" />}

                                        {result.indicators.setup_status.display}
                                    </div>
                                )}
                                <Button variant="ghost" size="sm" onClick={downloadReport} title="Download Report">
                                    <Download className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>

                        {/* Report Content */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4 prose prose-sm prose-invert max-w-none">
                            <ReactMarkdown
                                components={{
                                    h2: ({ node, ...props }) => <h2 className="text-lg font-bold text-primary mt-6 mb-3 border-b border-border/40 pb-1" {...props} />,
                                    ul: ({ node, ...props }) => <ul className="list-disc pl-5 space-y-1 text-muted-foreground" {...props} />,
                                    strong: ({ node, ...props }) => <strong className="text-foreground font-semibold" {...props} />,
                                    li: ({ node, ...props }) => <li className="text-muted-foreground" {...props} />,
                                    p: ({ node, ...props }) => <p className="leading-relaxed text-muted-foreground/90" {...props} />
                                }}
                            >
                                {result.raw}
                            </ReactMarkdown>
                        </div>

                        <div className="p-3 border-t border-border/50 bg-background shrink-0 flex justify-end">
                            <Button variant="outline" onClick={reset}>
                                Close
                            </Button>
                        </div>
                    </div>
                )}
            </DialogContent>
        </Dialog>
    )
}
