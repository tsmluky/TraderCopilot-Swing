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
                <Button variant="secondary" className="gap-2 shadow-sm border border-black/5 dark:border-white/10 bg-white dark:bg-secondary/50 text-foreground hover:bg-black/5 dark:hover:bg-secondary/80">
                    <ScrollText className="h-4 w-4 text-primary" />
                    Institutional Analysis
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[700px] max-h-[85vh] overflow-hidden flex flex-col p-0 gap-0 bg-white dark:bg-card border-black/5 dark:border-white/10 shadow-2xl">
                <DialogHeader className="p-5 border-b border-black/5 dark:border-white/5 bg-black/[0.02] dark:bg-white/[0.02]">
                    <div className="flex items-center justify-between pr-8">
                        <div className="flex items-center gap-3">
                            <div className="bg-primary/10 p-2 rounded-xl border border-primary/10 shadow-inner">
                                <FileText className="h-5 w-5 text-primary" />
                            </div>
                            <div className="space-y-0.5">
                                <DialogTitle className="text-xl">Institutional Analysis</DialogTitle>
                                <DialogDescription className="text-xs">
                                    Deep-dive quantitative & macro report (2-6 Weeks Horizon).
                                </DialogDescription>
                            </div>
                        </div>

                        {/* Language Toggle - Sleek & Premium */}
                        {!result && !loading && (
                            <div className="flex items-center gap-1 p-1 rounded-lg border border-black/5 dark:border-white/5 bg-black/5 dark:bg-black/20 backdrop-blur-sm">
                                <button
                                    onClick={() => setLanguage('en')}
                                    className={cn(
                                        "px-2.5 py-1 rounded-md transition-all duration-300 font-bold text-[10px]",
                                        language === 'en'
                                            ? "bg-white dark:bg-primary text-foreground dark:text-primary-foreground shadow-sm"
                                            : "text-muted-foreground hover:text-foreground hover:bg-black/5 dark:hover:bg-white/5"
                                    )}
                                >
                                    EN
                                </button>
                                <button
                                    onClick={() => setLanguage('es')}
                                    className={cn(
                                        "px-2.5 py-1 rounded-md transition-all duration-300 font-bold text-[10px]",
                                        language === 'es'
                                            ? "bg-white dark:bg-primary text-foreground dark:text-primary-foreground shadow-sm"
                                            : "text-muted-foreground hover:text-foreground hover:bg-black/5 dark:hover:bg-white/5"
                                    )}
                                >
                                    ES
                                </button>
                            </div>
                        )}
                    </div>
                </DialogHeader>

                {!result ? (
                    <div className="grid gap-6 p-6">
                        {/* Token Selector - Horizontal Cards */}
                        <div className="space-y-3">
                            <Label className="text-sm font-medium text-foreground ml-1">Select Asset (PRO Universe)</Label>
                            <div className="flex items-center gap-3">
                                {SUPPORTED_TOKENS.map((t) => {
                                    const getColor = (token: string, selected: boolean) => {
                                        switch (token) {
                                            case 'BTC': return selected
                                                ? "bg-orange-500/10 border-orange-500 text-orange-500 shadow-[0_0_15px_rgba(249,115,22,0.15)]"
                                                : "hover:border-orange-500/30 hover:bg-orange-500/5 hover:text-orange-500";
                                            case 'ETH': return selected
                                                ? "bg-indigo-500/10 border-indigo-500 text-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.15)]"
                                                : "hover:border-indigo-500/30 hover:bg-indigo-500/5 hover:text-indigo-400";
                                            case 'SOL': return selected
                                                ? "bg-teal-500/10 border-teal-500 text-teal-400 shadow-[0_0_15px_rgba(20,184,166,0.15)]"
                                                : "hover:border-teal-500/30 hover:bg-teal-500/5 hover:text-teal-400";
                                            case 'BNB': return selected
                                                ? "bg-yellow-500/10 border-yellow-500 text-yellow-500 shadow-[0_0_15px_rgba(234,179,8,0.15)]"
                                                : "hover:border-yellow-500/30 hover:bg-yellow-500/5 hover:text-yellow-500";
                                            case 'XRP': return selected
                                                ? "bg-blue-500/10 border-blue-500 text-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.15)]"
                                                : "hover:border-blue-500/30 hover:bg-blue-500/5 hover:text-blue-400";
                                            default: return selected
                                                ? "bg-primary text-primary-foreground"
                                                : "hover:border-primary/50 hover:bg-primary/5 hover:text-primary";
                                        }
                                    }

                                    return (
                                        <button
                                            key={t}
                                            onClick={() => !loading && setToken(t)}
                                            disabled={loading}
                                            className={cn(
                                                "flex-1 h-12 rounded-xl border flex items-center justify-center transition-all duration-200",
                                                loading ? "opacity-50 cursor-not-allowed" : "cursor-pointer",
                                                token === t
                                                    ? "translate-y-[-2px] ring-1 ring-transparent font-bold"
                                                    : "bg-white dark:bg-secondary/30 border-black/5 dark:border-white/5 text-muted-foreground",
                                                getColor(t, token === t)
                                            )}
                                        >
                                            <span className="text-sm tracking-tight">
                                                {t}
                                            </span>
                                        </button>
                                    )
                                })}
                            </div>
                        </div>

                        <Button
                            onClick={handleScan}
                            disabled={loading}
                            className="w-full mt-2 h-12 text-sm font-bold shadow-lg shadow-primary/20 rounded-xl transition-all hover:scale-[1.01] active:scale-[0.99] bg-primary text-primary-foreground hover:bg-primary/90"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Analyzing Institutional Data...
                                </>
                            ) : (
                                'Generate Institutional Report'
                            )}
                        </Button>

                        <div className="p-4 bg-black/[0.02] dark:bg-white/[0.02] rounded-xl border border-black/5 dark:border-white/5 text-xs text-muted-foreground space-y-3 mt-1">
                            <p className="font-bold text-foreground flex items-center gap-2">
                                <FileText className="h-3.5 w-3.5 text-primary" />
                                Report Scope:
                            </p>
                            <ul className="grid grid-cols-2 gap-y-2 gap-x-4 pl-1">
                                <li className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-primary/50" /> Strategy Thesis</li>
                                <li className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-primary/50" /> Macro Regime</li>
                                <li className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-primary/50" /> Market Structure</li>
                                <li className="flex items-center gap-2"><div className="w-1 h-1 rounded-full bg-primary/50" /> Bull/Bear Scenarios</li>
                            </ul>
                        </div>
                    </div>
                ) : (
                    <div className="flex-1 overflow-hidden flex flex-col min-h-0 bg-white dark:bg-black/20">
                        {/* Header Metrics */}
                        <div className="flex items-center justify-between p-3 px-5 bg-black/[0.02] dark:bg-white/[0.02] border-b border-black/5 dark:border-white/5 shrink-0">
                            <div className="flex items-center gap-3 text-sm">
                                <span className="font-black text-lg text-primary">{token}</span>
                                <div className="h-4 w-px bg-black/10 dark:bg-white/10" />
                                <span className="text-muted-foreground font-medium">Horizon: {result.indicators?.horizon || "2-6 Weeks"}</span>
                            </div>

                            <div className="flex items-center gap-2">
                                {/* Setup Status Badge */}
                                {result.indicators?.setup_status && (
                                    <div className={cn(
                                        "px-2.5 py-1 rounded-lg text-[10px] font-bold border flex items-center gap-1.5 uppercase tracking-wider",
                                        result.indicators.setup_status.decision === 'confluence'
                                            ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
                                            : result.indicators.setup_status.decision === 'neutral_no_setup'
                                                ? "bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 border-yellow-500/20"
                                                : "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20"
                                    )}>
                                        {result.indicators.setup_status.decision === 'confluence' ? <CheckCircle2 className="h-3 w-3" /> :
                                            result.indicators.setup_status.decision === 'neutral_no_setup' ? <AlertTriangle className="h-3 w-3" /> :
                                                <XCircle className="h-3 w-3" />}

                                        {result.indicators.setup_status.display}
                                    </div>
                                )}
                                <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-black/5 dark:hover:bg-white/5" onClick={downloadReport} title="Download Report">
                                    <Download className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>

                        {/* Report Content */}
                        <div className="flex-1 overflow-y-auto p-5 scrollbar-thin scrollbar-thumb-primary/10 hover:scrollbar-thumb-primary/20">
                            <div className="prose prose-sm dark:prose-invert max-w-none 
                                prose-headings:font-bold prose-headings:tracking-tight prose-headings:text-foreground
                                prose-h2:text-lg prose-h2:mt-6 prose-h2:mb-4 prose-h2:pb-2 prose-h2:border-b prose-h2:border-black/5 dark:prose-h2:border-white/5
                                prose-p:text-muted-foreground prose-p:leading-7
                                prose-li:text-muted-foreground
                                prose-strong:text-foreground prose-strong:font-semibold
                                prose-code:bg-black/5 dark:prose-code:bg-white/5 prose-code:px-1 prose-code:rounded prose-code:before:content-none prose-code:after:content-none
                            ">
                                <ReactMarkdown
                                    components={{
                                        h2: ({ ...props }) => (
                                            <div className="mt-8 first:mt-2 mb-4 pb-3 border-b border-black/5 dark:border-white/5 group">
                                                <h2 className="text-lg font-bold flex items-center gap-2 text-foreground" {...props}>
                                                    <span className="w-1.5 h-5 rounded-full bg-primary/60 group-hover:bg-primary transition-colors" />
                                                    {props.children}
                                                </h2>
                                            </div>
                                        ),
                                        strong: ({ ...props }) => (
                                            <strong className="font-bold text-foreground dark:text-white" {...props} />
                                        ),
                                        ul: ({ ...props }) => (
                                            <ul className="space-y-2.5 my-4" {...props} />
                                        ),
                                        li: ({ ...props }) => (
                                            <li className="flex gap-3 text-sm text-muted-foreground leading-relaxed">
                                                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/40 block" />
                                                <div className="flex-1">{props.children}</div>
                                            </li>
                                        ),
                                        p: ({ ...props }) => (
                                            <p className="leading-7 text-muted-foreground mb-4 last:mb-0 text-[0.95rem] text-pretty" {...props} />
                                        ),
                                        blockquote: ({ ...props }) => (
                                            <blockquote className="border-l-2 border-primary/30 pl-4 italic text-muted-foreground my-4 bg-primary/5 py-2 pr-2 rounded-r-lg" {...props} />
                                        )
                                    }}
                                >
                                    {result.raw}
                                </ReactMarkdown>
                            </div>
                        </div>

                        <div className="p-3 border-t border-black/5 dark:border-white/5 bg-black/[0.02] dark:bg-white/[0.02] shrink-0 flex justify-end">
                            <Button variant="ghost" className="hover:bg-black/5 dark:hover:bg-white/5 text-muted-foreground hover:text-foreground" onClick={reset}>
                                Close Analysis
                            </Button>
                        </div>
                    </div>
                )}
            </DialogContent>
        </Dialog>
    )
}
