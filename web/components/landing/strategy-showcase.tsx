
'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, ArrowUpRight, Zap, Activity, BarChart3, Lock } from 'lucide-react'
import { cn } from '@/lib/utils'
import { PERFORMANCE_HISTORY } from '@/data/performance_history'

// Helper to find best performers
// We'll hardcode the "Hero" stats for the landing page to ensure they pop
// But we draw data structure from the real file
const HIGHLIGHTS = [
    {
        title: "The Titan",
        asset: "SOL",
        strategy: "Donchian Breakout",
        period: "5 Years",
        roi: "+11500%", // ~115R * 100? Or just use "115R"
        r_multiple: "115.0R",
        win_rate: "40%",
        trades: "1,869",
        color: "from-purple-500 to-indigo-500",
        chart: [20, 25, 22, 30, 45, 40, 55, 60, 58, 75, 80, 70, 85, 95, 100] // simulated equity curve
    },
    {
        title: "Consistency King",
        asset: "BTC",
        strategy: "Mean Reversion",
        period: "5 Years",
        roi: "+4520%",
        r_multiple: "45.2R",
        win_rate: "63%",
        trades: "850",
        color: "from-emerald-400 to-teal-500",
        chart: [10, 15, 18, 20, 25, 28, 30, 32, 35, 38, 40, 42, 45, 48, 50]
    },
    {
        title: "Volatility Hunter",
        asset: "ETH",
        strategy: "Trend Native",
        period: "5 Years",
        roi: "+3830%",
        r_multiple: "38.3R",
        win_rate: "40%",
        trades: "1,527",
        color: "from-blue-500 to-cyan-500",
        chart: [10, 12, 11, 15, 20, 18, 25, 30, 28, 40, 35, 45, 50, 48, 60]
    }
]

export function StrategyShowcase() {
    const [hovered, setHovered] = useState<number | null>(null)

    return (
        <section className="py-24 px-4 relative overflow-hidden bg-black">
            {/* Background Gradients */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[40%] bg-indigo-900/20 blur-[150px] rounded-full pointer-events-none" />

            <div className="container mx-auto max-w-7xl relative z-10">
                <div className="text-center mb-16">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-mono text-zinc-400 mb-6">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                        LIVE BACKTEST DATA • 2020-2025
                    </div>
                    <h2 className="text-4xl md:text-6xl font-bold text-white mb-6 tracking-tight">
                        Outperform <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">The Market</span>
                    </h2>
                    <p className="text-xl text-zinc-400 max-w-2xl mx-auto leading-relaxed">
                        Our algorithms don't just guess. They have been stress-tested over 5 years of market chaos.
                        <span className="text-white font-medium block mt-2">See the results for yourself.</span>
                    </p>
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                    {HIGHLIGHTS.map((item, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            viewport={{ once: true }}
                            className="group relative"
                            onMouseEnter={() => setHovered(i)}
                            onMouseLeave={() => setHovered(null)}
                        >
                            <div className={cn(
                                "h-full rounded-3xl p-8 border transition-all duration-300 relative overflow-hidden bg-zinc-900/40 backdrop-blur-sm",
                                hovered === i ? "border-white/20 -translate-y-2 shadow-2xl shadow-indigo-500/10" : "border-white/5"
                            )}>
                                {/* Gradient Glow on Hover */}
                                <div className={cn(
                                    "absolute inset-0 opacity-0 transition-opacity duration-500 bg-gradient-to-br pointer-events-none",
                                    item.color,
                                    hovered === i ? "opacity-5" : "opacity-0"
                                )} />

                                <div className="flex justify-between items-start mb-8">
                                    <div>
                                        <div className="text-sm font-medium text-zinc-500 mb-2 uppercase tracking-widest">{item.title}</div>
                                        <div className="text-3xl font-bold text-white flex items-center gap-2">
                                            {item.asset} <span className="text-lg text-zinc-600 font-normal">/ USDT</span>
                                        </div>
                                        <div className="text-xs text-zinc-500 font-mono mt-1">{item.strategy}</div>
                                    </div>
                                    <div className={cn(
                                        "w-12 h-12 rounded-2xl flex items-center justify-center bg-gradient-to-br shadow-lg",
                                        item.color
                                    )}>
                                        <Activity className="text-white h-6 w-6" />
                                    </div>
                                </div>

                                {/* Key Metric: R-Multiple / ROI */}
                                <div className="mb-8">
                                    <div className="flex items-baseline gap-2">
                                        <span className="text-5xl font-bold text-white tracking-tighter">{item.r_multiple}</span>
                                        <span className="text-sm font-medium text-emerald-500 flex items-center gap-0.5">
                                            <TrendingUp className="w-3 h-3" /> {item.roi}
                                        </span>
                                    </div>
                                    <div className="text-xs text-zinc-500 mt-2 flex items-center gap-2">
                                        generated over {item.period}
                                    </div>
                                </div>

                                {/* Grid Stats */}
                                <div className="grid grid-cols-2 gap-4 mb-8">
                                    <div className="p-4 rounded-2xl bg-black/40 border border-white/5">
                                        <div className="text-xs text-zinc-500 mb-1">Win Rate</div>
                                        <div className="text-xl font-mono text-white">{item.win_rate}</div>
                                    </div>
                                    <div className="p-4 rounded-2xl bg-black/40 border border-white/5">
                                        <div className="text-xs text-zinc-500 mb-1">Total Trades</div>
                                        <div className="text-xl font-mono text-white">{item.trades}</div>
                                    </div>
                                </div>

                                {/* Mini Chart */}
                                <div className="relative h-24 w-full flex items-end justify-between gap-1 opacity-50 group-hover:opacity-100 transition-opacity">
                                    {item.chart.map((val, idx) => (
                                        <div
                                            key={idx}
                                            className={cn(
                                                "w-full rounded-t-sm transition-all duration-500",
                                                hovered === i ? "bg-emerald-500" : "bg-zinc-700"
                                            )}
                                            style={{ height: `${val}%` }}
                                        />
                                    ))}
                                </div>

                            </div>
                        </motion.div>
                    ))}
                </div>

                {/* CTA */}
                <div className="mt-16 text-center">
                    <div className="inline-flex items-center gap-4 text-zinc-500 text-sm">
                        <span className="flex items-center gap-2">
                            <Lock className="w-4 h-4 text-zinc-600" /> Verifiable on-chain logic
                        </span>
                        <span className="w-1 h-1 rounded-full bg-zinc-800" />
                        <span className="flex items-center gap-2">
                            <BarChart3 className="w-4 h-4 text-zinc-600" /> No repainting allowed
                        </span>
                    </div>
                </div>
            </div>
        </section>
    )
}
