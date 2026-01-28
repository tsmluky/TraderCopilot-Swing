'use client'

import React, { useRef, useState, useEffect } from 'react'
import Image from 'next/image'
import { Activity, Cpu } from 'lucide-react'
import { cn } from '@/lib/utils'
import { SpotlightCard } from '@/components/ui/spotlight-card'

// INSTITUTIONAL-GRADE DATA
const STRATEGIES = [
    {
        id: 'stat-arb',
        title: 'Statistical Mean Reversion',
        tagline: 'Short-Term Alpha',
        visual: '/saas-trading-dashboard-dark.png',
        description: 'Exploits short-term pricing inefficiencies using Ornstein-Uhlenbeck processes. Executing mean-reversion trades when statistical deviation exceeds 2.5 sigma.',
        color: 'emerald',
        // HIGH WIN RATE, LOW AVG ROI (Scalping/Swing)
        stats: {
            winRate: '68.5%',
            profitFactor: '2.15',
            trades: '42/mo'
        },
        dashboard: {
            signals24h: 3,
            avgRoi: '+1.8%'
        },
        logic: [
            "# Calculate Z-Score deviation",
            "z_score = (price - rolling_mean) / rolling_std",
            "",
            "if z_score < -2.5 and regime == 'neutral':",
            "    size = calc_kelly_criterion(win_prob=0.65)",
            "    execute_limit_entry(price=bid*1.001)"
        ]
    },
    {
        id: 'trend-liquidity',
        title: 'Institutional Trend',
        tagline: 'Asymmetric Compounding',
        visual: '/hero-hologram.png',
        description: 'Captures multi-week liquidity runs. Filters range-bound noise using ADX and Volume Profiling. Designed to catch "fat tail" moves.',
        color: 'indigo',
        // LOW WIN RATE, MASSIVE AVG ROI (Trend Following)
        stats: {
            winRate: '42.1%',
            profitFactor: '3.8',
            trades: '22/mo'
        },
        dashboard: {
            signals24h: 0,
            avgRoi: '+14.5%'
        },
        logic: [
            "# Filter chop using ADX strength",
            "trend_strength = ta.adx(high, low, close, length=14)",
            "",
            "if close > donchian_high[20] and trend_strength > 25:",
            "    vol_target = target_exposure / current_atr",
            "    execute_breakout(size=vol_target)"
        ]
    },
    {
        id: 'vol-premia',
        title: 'Volatility Risk Premia',
        tagline: 'Gamma Expansion',
        visual: '/dense-platform.png',
        description: 'Harvests volatility risk premia during accumulation phases. Dynamically adjusts position sizing based on GARCH volatility forecasting.',
        color: 'violet',
        // BALANCED
        stats: {
            winRate: '54.3%',
            profitFactor: '1.9',
            trades: '15/mo'
        },
        dashboard: {
            signals24h: 1,
            avgRoi: '+3.2%'
        },
        logic: [
            "# Analyze Historical vs Implied Volatility",
            "hv_rank = percentileofscore(hv_history, current_hv)",
            "",
            "if hv_rank < 20 and volume_delta > 0:",
            "    # Anticipate expansion",
            "    enter_long_gamma_setup()"
        ]
    }
]

export function StrategyShowcase() {
    const [activeStrategy, setActiveStrategy] = useState(0)
    const cardRefs = useRef<(HTMLDivElement | null)[]>([])

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        const index = Number(entry.target.getAttribute('data-index'))
                        if (!isNaN(index)) {
                            setActiveStrategy(index)
                        }
                    }
                })
            },
            {
                root: null,
                rootMargin: '-40% 0px -40% 0px', // Adjusted for better trigger
                threshold: 0.2, // Trigger when 20% visible
            }
        )

        cardRefs.current.forEach((card) => {
            if (card) observer.observe(card)
        })

        return () => observer.disconnect()
    }, [])

    return (
        <section className="py-32 bg-black relative">
            {/* Background Gradients */}
            <div className="absolute top-0 right-0 w-[50%] h-[50%] bg-indigo-900/20 blur-[150px] rounded-full pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-[50%] h-[50%] bg-emerald-900/10 blur-[150px] rounded-full pointer-events-none" />


            <div className="container mx-auto px-4 max-w-6xl">

                {/* Section Header */}
                <div className="text-center mb-24 max-w-3xl mx-auto">
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 tracking-tight">
                        Proven Logic. <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">Verifiable Edge.</span>
                    </h2>
                    <p className="text-xl text-zinc-400 leading-relaxed">
                        We don't hide behind "AI black boxes". Our strategies are based on mathematical models you can read, audit, and understand.
                    </p>
                </div>

                <div className="flex flex-col lg:flex-row gap-24 relative">

                    {/* LEFT COLUMN: Scroll Triggers (Invisible triggers + Visible Cards) */}
                    <div className="lg:w-1/2 relative z-10 space-y-[80vh] py-[20vh] pl-4">
                        {/* Spacing increased to 80vh to guarantee long scroll time per item */}

                        {STRATEGIES.map((strategy, index) => (
                            <div
                                key={strategy.id}
                                data-index={index}
                                ref={el => { cardRefs.current[index] = el }}
                                className={`transition-all duration-500 ${activeStrategy === index
                                    ? 'opacity-100 translate-x-0'
                                    : 'opacity-30 blur-sm -translate-x-4'
                                    }`}
                            >
                                <SpotlightCard className="bg-zinc-900/80 backdrop-blur-md border-white/10 p-8 md:p-10 max-w-xl shadow-2xl" spotlightColor={strategy.color === 'emerald' ? 'rgba(16, 185, 129, 0.2)' : strategy.color === 'indigo' ? 'rgba(99, 102, 241, 0.2)' : 'rgba(139, 92, 246, 0.2)'}>
                                    <div className="flex items-center gap-3 mb-6">
                                        <div className="px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider bg-white/5 text-zinc-400 border border-white/5">
                                            0{index + 1} // {strategy.tagline}
                                        </div>
                                    </div>

                                    <h3 className="text-3xl font-bold text-white mb-4">{strategy.title}</h3>
                                    <p className="text-zinc-400 leading-relaxed mb-8">{strategy.description}</p>

                                    <div className="grid grid-cols-3 gap-4 border-t border-white/5 pt-6">
                                        <div>
                                            <div className="text-[10px] uppercase text-zinc-600 tracking-wider mb-1">Win Rate</div>
                                            <div className="text-xl font-mono text-white">{strategy.stats.winRate}</div>
                                        </div>
                                        <div>
                                            <div className="text-[10px] uppercase text-zinc-600 tracking-wider mb-1">Profit Factor</div>
                                            <div className="text-xl font-mono text-white">{strategy.stats.profitFactor}</div>
                                        </div>
                                        <div>
                                            <div className="text-[10px] uppercase text-zinc-600 tracking-wider mb-1">Trades</div>
                                            <div className="text-xl font-mono text-white">{strategy.stats.trades}</div>
                                        </div>
                                    </div>
                                </SpotlightCard>
                            </div>
                        ))}
                    </div>

                    {/* RIGHT COLUMN: Sticky Visualisation (The "Dashboard" Image) */}
                    <div className="lg:w-1/2 hidden lg:block relative">
                        <div className="sticky top-0 h-screen flex items-center justify-center">
                            {/* Visual Asset Container */}
                            <div className="relative w-full aspect-square max-h-[600px] flex items-center justify-center">

                                {STRATEGIES.map((strategy, index) => (
                                    <div
                                        key={strategy.id}
                                        className={`absolute inset-0 transition-all duration-700 ease-in-out flex items-center justify-center ${activeStrategy === index
                                            ? 'opacity-100 scale-100 rotate-0 delay-100'
                                            : 'opacity-0 scale-95 rotate-2 pointer-events-none'
                                            }`}
                                    >
                                        <div className="relative w-full h-auto aspect-[4/3] rounded-2xl overflow-hidden shadow-2xl border border-white/10 bg-[#09090b]">
                                            {/* Header */}
                                            <div className="absolute top-0 left-0 right-0 h-10 bg-black/50 border-b border-white/5 flex items-center justify-between px-4 z-20 backdrop-blur-md">
                                                <div className="text-[10px] font-mono text-zinc-500">ACTIVE_STRATEGY</div>
                                                <div className="text-xs font-bold text-white tracking-wide">{strategy.title}</div>
                                                <div className="text-[10px] font-mono text-zinc-500 opacity-50">v2.4.0_STABLE</div>
                                            </div>

                                            {/* Logic / Fake Code Overlay (Replaces Image) */}
                                            <div className="relative w-full h-full p-8 pt-16 font-mono text-xs text-zinc-400 bg-black/90">
                                                <div className="absolute top-14 right-6 text-[10px] text-zinc-600">LOGIC_PREVIEW.py</div>

                                                <div className="space-y-4">
                                                    <div className="flex gap-4">
                                                        <span className="text-zinc-700 select-none">01</span>
                                                        <span className="text-purple-400"># Strategy Logic Configuration</span>
                                                    </div>

                                                    {strategy.logic.map((line, lIdx) => (
                                                        <div key={lIdx} className="flex gap-4">
                                                            <span className="text-zinc-700 select-none text-[10px] pt-0.5">{String(lIdx + 10).padStart(2, '0')}</span>
                                                            <span className={cn(
                                                                "font-mono",
                                                                line.startsWith("#") ? "text-zinc-500 italic" :
                                                                    line.includes("if") || line.includes("def") || line.includes("return") ? "text-pink-400" :
                                                                        line.includes("=") || line.includes(">") ? "text-cyan-300" :
                                                                            "text-zinc-300"
                                                            )}>
                                                                {line}
                                                            </span>
                                                        </div>
                                                    ))}

                                                    <div className="flex gap-4 mt-8">
                                                        <span className="text-zinc-700 select-none">05</span>
                                                        <div className="flex items-center gap-2">
                                                            <span className="text-zinc-500">MARKET_SCANNER_STATUS:</span>
                                                            <div className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-[10px] uppercase">Active</div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>

                                        </div>
                                    </div>
                                ))}

                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </section>
    )
}
