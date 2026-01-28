'use client'

import { useRef, useState } from 'react'
import { Activity, Shield, Zap, Layers, BarChart3, Lock } from 'lucide-react'
import { cn } from '@/lib/utils'

function FeatureCard({ title, description, icon: Icon, className, children }: any) {
    const divRef = useRef<HTMLDivElement>(null)
    const [isFocused, setIsFocused] = useState(false)
    const [position, setPosition] = useState({ x: 0, y: 0 })
    const [opacity, setOpacity] = useState(0)

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!divRef.current) return

        const div = divRef.current
        const rect = div.getBoundingClientRect()

        setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top })
    }

    const handleFocus = () => {
        setIsFocused(true)
        setOpacity(1)
    }

    const handleBlur = () => {
        setIsFocused(false)
        setOpacity(0)
    }

    const handleMouseEnter = () => {
        setOpacity(1)
    }

    const handleMouseLeave = () => {
        setOpacity(0)
    }

    return (
        <div
            ref={divRef}
            onMouseMove={handleMouseMove}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            className={cn(
                "relative group rounded-3xl border border-white/5 bg-zinc-900/80 backdrop-blur-sm overflow-hidden min-h-[300px] flex flex-col p-8 transition-colors hover:border-emerald-500/30 hover:bg-zinc-900/90",
                className
            )}
        >
            {/* Hover Spotlight Gradient */}
            <div
                className="absolute -inset-px transition-opacity duration-300 pointer-events-none"
                style={{
                    opacity,
                    background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, rgba(16, 185, 129, 0.15), transparent 40%)`
                }}
            />

            {/* Content */}
            <div className="relative z-10 flex flex-col h-full">
                <div className="mb-6 inline-flex p-3 rounded-2xl bg-white/5 text-emerald-400 group-hover:scale-110 transition-transform duration-500 w-fit">
                    <Icon className="w-6 h-6" />
                </div>

                <h3 className="text-2xl font-bold text-white mb-3">{title}</h3>
                <p className="text-zinc-400 leading-relaxed mb-8 flex-grow">{description}</p>

                {/* Interactive Visual Area */}
                <div className="relative w-full h-32 mt-auto rounded-xl bg-black/50 overflow-hidden border border-white/5 group-hover:border-emerald-500/30 transition-colors">
                    {/* Scanline Effect */}
                    <div className={cn(
                        "absolute top-0 left-0 w-full h-[2px] bg-emerald-500/50 shadow-[0_0_20px_rgba(16,185,129,0.5)] transition-all duration-[2s] ease-in-out",
                        opacity > 0 ? "top-full" : "top-0"
                    )} />

                    {children}
                </div>
            </div>
        </div>
    )
}

export function PremiumFeatures() {
    return (
        <section id="features" className="py-32 relative overflow-hidden">
            {/* Background Elements */}
            <div className="absolute top-[20%] left-0 w-[500px] h-[500px] bg-indigo-500/5 blur-[120px] rounded-full pointer-events-none" />

            <div className="container mx-auto px-4 max-w-7xl">

                <div className="text-center mb-20 max-w-3xl mx-auto">
                    <h2 className="text-4xl md:text-6xl font-bold text-white mb-6 tracking-tight">
                        Engineered for <span className="text-emerald-400">Precision.</span>
                    </h2>
                    <p className="text-lg text-zinc-400">
                        Automated analysis. Human execution. A system designed to filter noise and deliver pure signal.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-6 gap-6">

                    {/* Row 1 */}
                    {/* Feature 4: Instant Alerts (2 cols) - Moved to Top Left */}
                    <FeatureCard
                        title="Instant Alerts"
                        description="Get notified via Telegram the second a setup is confirmed. Never miss a move."
                        icon={Zap}
                        className="md:col-span-2 min-h-[320px]"
                    >
                        {/* Visual: Notification Pulse */}
                        <div className="absolute inset-0 flex items-center justify-center">
                            <div className="relative">
                                <div className="w-3 h-3 bg-emerald-500 rounded-full animate-ping absolute inset-0" />
                                <div className="w-3 h-3 bg-white rounded-full relative z-10" />
                            </div>
                            <div className="ml-4 text-xs font-mono text-white">New Signal: BTC/USDT</div>
                        </div>
                    </FeatureCard>

                    {/* Feature 1: Algorithmic Detection (Large - 4 cols) - Moved to Top Right */}
                    <FeatureCard
                        title="Algorithmic Detection"
                        description="Our engines scan major liquid pairs simultaneously using 3 distinct logic models. We filter out 99% of the noise so you only see high-probability setups."
                        icon={Activity}
                        className="md:col-span-4 min-h-[320px]"
                    >
                        {/* Visual: Radar Scan */}
                        <div className="absolute inset-0 flex items-center justify-center opacity-50">
                            <div className="w-[200px] h-[200px] border border-emerald-500/20 rounded-full flex items-center justify-center animate-[spin_4s_linear_infinite]">
                                <div className="w-[10px] h-[10px] bg-emerald-500 rounded-full absolute top-2 right-10 shadow-[0_0_10px_#10b981]" />
                            </div>
                            <div className="absolute w-[140px] h-[140px] border border-white/5 rounded-full" />
                            <div className="absolute w-[80px] h-[80px] border border-white/5 rounded-full" />
                        </div>
                    </FeatureCard>

                    {/* Row 2 */}
                    {/* Feature 2: Multi-Timeframe (Wide - 4 cols) - Bottom Left */}
                    <FeatureCard
                        title="Timeframe Confluence"
                        description="We don't just look at one chart. The engine cross-references Daily trends with 4H and 1H triggers to ensure you are trading with the flow, not against it."
                        icon={Layers}
                        className="md:col-span-4 min-h-[320px]"
                    >
                        {/* Visual: Horizontal Stacked Layers */}
                        <div className="absolute inset-0 flex items-center justify-center p-6">
                            <div className="flex gap-4 w-full justify-center items-end">
                                <div className="flex-1 max-w-[180px] h-20 border border-emerald-500/30 bg-emerald-500/5 rounded p-3 flex flex-col justify-between">
                                    <span className="text-[10px] text-zinc-500 font-mono">1D TREND</span>
                                    <span className="text-sm text-emerald-400 font-bold tracking-wider">BULLISH</span>
                                </div>
                                <div className="flex-1 max-w-[180px] h-20 border border-white/10 bg-white/5 rounded p-3 flex flex-col justify-between">
                                    <span className="text-[10px] text-zinc-500 font-mono">4H MOMENTUM</span>
                                    <span className="text-sm text-zinc-300 font-bold tracking-wider">NEUTRAL</span>
                                </div>
                                <div className="flex-1 max-w-[180px] h-20 border border-emerald-500/30 bg-emerald-500/5 rounded p-3 flex flex-col justify-between shadow-[0_0_15px_rgba(16,185,129,0.1)]">
                                    <span className="text-[10px] text-zinc-500 font-mono">1H TRIGGER</span>
                                    <span className="text-sm text-emerald-400 font-bold tracking-wider animate-pulse">FIRED</span>
                                </div>
                            </div>
                        </div>
                    </FeatureCard>

                    {/* Feature 3: Risk Management (2 cols) - Bottom Right */}
                    <FeatureCard
                        title="Built-in R.M."
                        description="Every signal comes with calculated Stop Loss and Take Profit levels based on volatility (ATR)."
                        icon={Shield}
                        className="md:col-span-2 min-h-[320px]"
                    >
                        {/* Visual: Shield / Range */}
                        <div className="absolute inset-0 flex items-center justify-center font-mono text-xs">
                            <div className="space-y-2">
                                <div className="text-emerald-400">TP: $102,450</div>
                                <div className="w-32 h-1 bg-white/10 rounded-full overflow-hidden">
                                    <div className="w-[60%] h-full bg-emerald-500" />
                                </div>
                                <div className="text-red-400">SL: $94,200</div>
                            </div>
                        </div>
                    </FeatureCard>

                </div>
            </div>
        </section>
    )
}
