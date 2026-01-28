'use client'

import React from 'react'
import Image from 'next/image'
import { TrendingUp, ArrowRight, Activity, ShieldCheck, BarChart3, Search, Bell, Menu, Cpu } from 'lucide-react'
import { SpotlightCard } from '@/components/ui/spotlight-card'
import { cn } from '@/lib/utils'

export function HeroMockup() {
    return (
        <div className="relative mx-auto max-w-[1240px] w-full mt-16 px-4 sm:px-0 opacity-0 animate-fade-up delay-200 perspective-[2000px] group" style={{ animationFillMode: 'forwards' }}>

            {/* 1. Technical Grid Background (Subtle) */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-[url('/grid-pattern.svg')] opacity-[0.03] -z-10" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[100%] h-[100%] bg-emerald-500/5 blur-[150px] -z-10" />

            {/* Abstract Background Grid (The "Floor") */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-[40%] w-[100vw] h-[800px] bg-[linear-gradient(to_right,#1f2937_1px,transparent_1px),linear-gradient(to_bottom,#1f2937_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-20 pointer-events-none transform perspective-[1000px] rotate-x-60" />

            {/* Floating Card 1: Scanner Logic (Left) */}
            <div className="absolute top-0 left-[10%] z-30 w-72 opacity-0 animate-fade-right delay-500 fill-mode-forwards">
                <div className="rounded-xl border border-white/10 bg-black/40 backdrop-blur-md p-5 shadow-2xl font-mono hover:bg-black/60 transition-colors cursor-default">
                    <div className="flex justify-between items-center mb-4 border-b border-white/5 pb-2">
                        <span className="text-[10px] text-zinc-500 font-medium uppercase tracking-widest">Live Scanner</span>
                        <div className="flex gap-1.5 items-center">
                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            <span className="text-[10px] text-emerald-500">Scanning</span>
                        </div>
                    </div>

                    {/* Scanner Lines */}
                    <div className="space-y-2 text-[11px]">
                        <div className="flex justify-between items-center">
                            <span className="text-zinc-500">SOL/USDT</span>
                            <span className="text-zinc-600">Checking Volatility...</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-zinc-500">ETH/USDT</span>
                            <span className="text-zinc-600">Checking RSI...</span>
                        </div>
                        <div className="flex justify-between items-center p-1.5 bg-emerald-500/5 border-l-2 border-emerald-500">
                            <span className="text-zinc-300 font-bold">BTC/USDT</span>
                            <span className="text-emerald-500 font-bold">SETUP FOUND</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Floating Card 2: Strategy Engine (Right) */}
            <div className="absolute top-20 right-[10%] z-40 w-80 opacity-0 animate-fade-left delay-700 fill-mode-forwards">
                <div className="rounded-xl border border-white/10 bg-black/40 backdrop-blur-md shadow-2xl overflow-hidden font-mono hover:bg-black/60 transition-colors cursor-default">
                    {/* Header */}
                    <div className="px-5 py-3 border-b border-white/5 flex items-center justify-between bg-white/[0.01]">
                        <div className="flex items-center gap-2">
                            <Cpu className="w-3.5 h-3.5 text-zinc-400" />
                            <div className="font-mono text-xs text-zinc-300">Logic Core</div>
                        </div>
                        <div className="text-[10px] text-zinc-600 font-mono">THREAD_01</div>
                    </div>

                    {/* Logic Visual */}
                    <div className="p-5 text-xs space-y-3">
                        <div className="flex items-center gap-3">
                            <div className="h-4 w-0.5 bg-zinc-800" />
                            <span className="text-zinc-500 min-w-[60px]">SIGNAL</span>
                            <span className="text-emerald-400">RSI(14) &lt; 30</span>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="h-4 w-0.5 bg-zinc-800" />
                            <span className="text-zinc-500 min-w-[60px]">CONFIRM</span>
                            <span className="text-emerald-400">Vol Spike &gt; 2.5x</span>
                        </div>

                        <div className="mt-4 pt-3 border-t border-white/5 flex justify-between items-center">
                            <span className="text-zinc-500">Action</span>
                            <span className="text-black font-bold bg-emerald-500 px-3 py-1 rounded-sm text-[10px] tracking-wide">EXECUTE</span>
                        </div>
                    </div>
                </div>
            </div>

        </div >
    )
}
