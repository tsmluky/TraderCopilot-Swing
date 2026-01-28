'use client'

import React, { useState } from 'react'
import { FileText, Download, CheckCircle2, Lock, FileSpreadsheet } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { SpotlightCard } from '@/components/ui/spotlight-card'
import { toast } from 'sonner'

const AUDIT_FILES = [
    {
        id: 'btc-mr',
        name: 'BTC_MeanReversion_1H_5Y.txt',
        size: '142 KB',
        date: 'Jan 28, 2026',
        type: 'txt',
        path: '/audit-logs/BTC_MeanReversion_1H_5Y.txt'
    },
    {
        id: 'eth-tb',
        name: 'ETH_TitanBreakout_1H_5Y.txt',
        size: '128 KB',
        date: 'Jan 28, 2026',
        type: 'txt',
        path: '/audit-logs/ETH_TitanBreakout_1H_5Y.txt'
    },
    {
        id: 'sol-mr',
        name: 'SOL_MeanReversion_1H_5Y.txt',
        size: '115 KB',
        date: 'Jan 27, 2026',
        type: 'txt',
        path: '/audit-logs/SOL_MeanReversion_1H_5Y.txt'
    },
    {
        id: 'bnb-mr',
        name: 'BNB_MeanReversion_1H_5Y.txt',
        size: '136 KB',
        date: 'Jan 27, 2026',
        type: 'txt',
        path: '/audit-logs/BNB_MeanReversion_1H_5Y.txt'
    },
    {
        id: 'xrp-tb',
        name: 'XRP_TitanBreakout_1H_5Y.txt',
        size: '94 KB',
        date: 'Jan 26, 2026',
        type: 'txt',
        path: '/audit-logs/XRP_TitanBreakout_1H_5Y.txt'
    }
]

export function TransparencyHub() {
    const [downloading, setDownloading] = useState<string | null>(null)

    const handleDownload = async (file: typeof AUDIT_FILES[0]) => {
        setDownloading(file.id)

        try {
            // Simulate network delay for "weight"
            await new Promise(resolve => setTimeout(resolve, 800))

            // Fetch real file content from public folder
            const response = await fetch(file.path)
            const txtContent = await response.text()

            const blob = new Blob([txtContent], { type: 'text/plain;charset=utf-8;' })
            const url = URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', file.name)
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)

            toast.success(`Downloaded ${file.name} successfully`)
        } catch (error) {
            toast.error("Download failed. Please try again.")
        } finally {
            setDownloading(null)
        }
    }

    return (
        <section id="transparency" className="py-24 relative overflow-hidden">
            {/* Background Mesh */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />

            <div className="container mx-auto px-4 max-w-6xl relative z-10">
                <div className="flex flex-col lg:flex-row gap-16 items-center">

                    {/* Left: Copy */}
                    <div className="flex-1 space-y-8">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono font-medium tracking-wider">
                            <CheckCircle2 className="w-3 h-3" />
                            RADICAL TRANSPARENCY
                        </div>

                        <h2 className="text-4xl md:text-5xl font-bold text-white tracking-tight">
                            We don't ask for trust. <br />
                            <span className="text-zinc-500">We provide proof.</span>
                        </h2>

                        <p className="text-lg text-zinc-400 leading-relaxed max-w-xl">
                            In an industry full of photoshopped PnL and deleted tweets, we stand apart.
                            Every signal is recorded on-chain. Every backtest uses tick-level data including fees and slippage.
                        </p>

                        <div className="space-y-4 pt-4">
                            <div className="flex gap-4">
                                <div className="w-12 h-12 rounded-xl bg-zinc-900 border border-white/5 flex items-center justify-center flex-shrink-0">
                                    <CheckCircle2 className="w-6 h-6 text-emerald-500" />
                                </div>
                                <div>
                                    <h4 className="text-white font-bold mb-1">No Repainting</h4>
                                    <p className="text-sm text-zinc-400">Our backtester is "Bar-Close" strictly. Signals are never removed after the fact.</p>
                                </div>
                            </div>
                            <div className="flex gap-4">
                                <div className="w-12 h-12 rounded-xl bg-zinc-900 border border-white/5 flex items-center justify-center flex-shrink-0">
                                    <FileSpreadsheet className="w-6 h-6 text-emerald-500" />
                                </div>
                                <div>
                                    <h4 className="text-white font-bold mb-1">Raw TXT Export</h4>
                                    <p className="text-sm text-zinc-400">Don't take our word for it. Download the raw TXT logs and verify the timestamps yourself.</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Right: The "Vault" */}
                    <div className="flex-1 w-full max-w-md">
                        <SpotlightCard className="bg-zinc-900/40 border-zinc-800" spotlightColor="rgba(255, 255, 255, 0.05)">
                            <div className="p-1">
                                <div className="bg-black/50 rounded-xl border border-white/5 overflow-hidden">
                                    {/* Header */}
                                    <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between bg-zinc-900/50">
                                        <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider">Public Audit Vault</span>
                                        <div className="flex items-center gap-1.5">
                                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                            <span className="text-[10px] font-bold text-emerald-500">VERIFIED LIVE</span>
                                        </div>
                                    </div>

                                    {/* File List */}
                                    <div className="divide-y divide-white/5">
                                        {AUDIT_FILES.map((file) => (
                                            <div key={file.id} className="p-4 flex items-center justify-between group hover:bg-white/[0.02] transition-colors">
                                                <div className="flex items-center gap-4">
                                                    <div className="w-10 h-10 rounded-lg bg-zinc-900 border border-white/5 flex items-center justify-center group-hover:border-emerald-500/20 transition-colors">
                                                        <FileText className="w-5 h-5 text-zinc-500 group-hover:text-emerald-400 transition-colors" />
                                                    </div>
                                                    <div>
                                                        <div className="text-sm text-white font-medium group-hover:text-emerald-300 transition-colors truncate max-w-[180px]">
                                                            {file.name}
                                                        </div>
                                                        <div className="flex items-center gap-2 text-[10px] text-zinc-500 font-mono">
                                                            <span>{file.type.toUpperCase()}</span>
                                                            <span>•</span>
                                                            <span>{file.size}</span>
                                                            <span>•</span>
                                                            <span>{file.date}</span>
                                                        </div>
                                                    </div>
                                                </div>

                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="text-zinc-500 hover:text-white hover:bg-white/5"
                                                    onClick={() => handleDownload(file)}
                                                    disabled={!!downloading}
                                                >
                                                    {downloading === file.id ? (
                                                        <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                                                    ) : (
                                                        <Download className="w-5 h-5" />
                                                    )}
                                                </Button>
                                            </div>
                                        ))}
                                    </div>


                                </div>
                            </div>
                        </SpotlightCard>
                    </div>

                </div>
            </div>
        </section>
    )
}
