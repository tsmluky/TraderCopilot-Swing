'use client'

import React from 'react'
import { MessageSquare, Bell, Zap, BrainCircuit, Check, Smartphone } from 'lucide-react'
import { cn } from '@/lib/utils'
import { SpotlightCard } from '@/components/ui/spotlight-card'

export function CopilotFeatures() {
    return (
        <section className="py-32 relative border-t border-white/5 overflow-hidden">

            {/* Background Effects */}
            <div className="absolute top-1/2 right-0 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/10 blur-[150px] rounded-full pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-purple-500/5 blur-[120px] rounded-full pointer-events-none" />

            <div className="container mx-auto px-4 max-w-7xl relative z-10">

                {/* Header */}
                <div className="text-center max-w-3xl mx-auto mb-20 animate-fade-up">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-medium text-indigo-400 mb-6">
                        <BrainCircuit className="w-3 h-3" />
                        AI CO-PILOT ARCHITECTURE
                    </div>
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                        Never Miss a Move.<br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">Never Trade Alone.</span>
                    </h2>
                    <p className="text-lg text-zinc-400 leading-relaxed">
                        Markets act fast. You need to act faster.
                        Our system alerts you the microsecond a setup confirms, and our AI answers your questions 24/7.
                    </p>
                </div>

                <div className="grid lg:grid-cols-2 gap-12 items-center">

                    {/* FEATURE 1: Instant Telegram Alerts (The "Action" side) */}
                    <SpotlightCard className="bg-zinc-900/50 border-white/10 overflow-hidden group" spotlightColor="rgba(168, 85, 247, 0.15)">
                        <div className="p-8 md:p-12 relative min-h-[500px] flex flex-col">
                            {/* Decorative Mobile Frame mock */}
                            <div className="absolute top-12 right-12 w-64 md:w-72 bg-black/90 border border-zinc-800 rounded-3xl shadow-2xl rotate-[-5deg] group-hover:rotate-0 transition-transform duration-700 ease-out z-10 p-4">
                                {/* Notch */}
                                <div className="absolute top-0 left-1/2 -translate-x-1/2 h-6 w-24 bg-black rounded-b-xl z-20" />

                                {/* Notification Item */}
                                <div className="mt-8 bg-zinc-800/80 backdrop-blur-md rounded-2xl p-4 border border-white/5 shadow-lg mb-4 opacity-0 animate-fade-in delay-300 fill-mode-forwards">
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center gap-2">
                                            <div className="w-5 h-5 rounded bg-[#229ED9] flex items-center justify-center">
                                                <Zap className="w-3 h-3 text-white" />
                                            </div>
                                            <span className="text-[10px] uppercase font-bold text-zinc-400">TELEGRAM • NOW</span>
                                        </div>
                                    </div>
                                    <div className="text-sm font-semibold text-white mb-1">🚨 LONG: SOL/USDT Confirmed</div>
                                    <div className="text-xs text-zinc-400">Mean Reversion Trigger fired on 1H. Entry Zone: $142.50. Risk: 1.5%.</div>
                                </div>

                                {/* Notification Item 2 */}
                                <div className="bg-zinc-800/80 backdrop-blur-md rounded-2xl p-4 border border-white/5 shadow-lg opacity-0 animate-fade-in delay-700 fill-mode-forwards opacity-60 scale-95">
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center gap-2">
                                            <div className="w-5 h-5 rounded bg-[#229ED9] flex items-center justify-center">
                                                <Zap className="w-3 h-3 text-white" />
                                            </div>
                                            <span className="text-[10px] uppercase font-bold text-zinc-400">TELEGRAM • 15M AGO</span>
                                        </div>
                                    </div>
                                    <div className="text-sm font-semibold text-white mb-1">Take Profit Reached 🎯</div>
                                    <div className="text-xs text-zinc-400">BTC Position closed at $98,400. PnL: +4.2R.</div>
                                </div>
                            </div>

                            {/* Content */}
                            <div className="mt-auto relative z-20 max-w-sm">
                                <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-6">
                                    <Bell className="w-6 h-6 text-purple-400" />
                                </div>
                                <h3 className="text-2xl font-bold text-white mb-4">Instant Execution Alerts</h3>
                                <p className="text-zinc-400 text-sm mb-6">
                                    Connect your Telegram in 1 click. We push buy/sell signals, stop-loss adjustments, and take-profit notifications directly to your phone.
                                </p>
                                <ul className="space-y-3">
                                    <li className="flex items-center gap-3 text-sm text-zinc-300">
                                        <Check className="w-4 h-4 text-emerald-500" /> <span className="font-medium text-white">Sub-100ms Latency</span>
                                    </li>
                                    <li className="flex items-center gap-3 text-sm text-zinc-300">
                                        <Check className="w-4 h-4 text-emerald-500" /> <span className="font-medium text-white">Actionable Levels (Entry, SL, TP)</span>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </SpotlightCard>


                    {/* FEATURE 2: AI Advisor Chat (The "Intelligence" side) */}
                    <SpotlightCard className="bg-zinc-900/50 border-white/10 overflow-hidden group" spotlightColor="rgba(99, 102, 241, 0.15)">
                        <div className="p-8 md:p-12 relative min-h-[500px] flex flex-col">

                            {/* Chat UI Mock */}
                            <div className="absolute top-12 left-12 w-full max-w-md bg-[#09090b] border border-zinc-800 rounded-tl-3xl rounded-bl-3xl shadow-2xl z-10 p-6 opacity-90 group-hover:translate-x-2 transition-transform duration-700">
                                {/* AI Message */}
                                <div className="flex gap-4 mb-6">
                                    <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center shrink-0 shadow-[0_0_10px_rgba(99,102,241,0.5)]">
                                        <BrainCircuit className="w-4 h-4 text-white" />
                                    </div>
                                    <div className="bg-zinc-800/50 rounded-2xl rounded-tl-none p-4 border border-white/5">
                                        <p className="text-xs text-zinc-300 leading-relaxed">
                                            I've analyzed the BTC 4H chart. We are seeing a bullish divergence on RSI, but volume is declining. <span className="text-white font-medium">Recommendation: Wait for a break above $98,200 before adding to your long.</span>
                                        </p>
                                    </div>
                                </div>
                                {/* User Message */}
                                <div className="flex gap-4 mb-6 flex-row-reverse">
                                    <div className="bg-indigo-600/20 rounded-2xl rounded-tr-none p-3 border border-indigo-500/20">
                                        <p className="text-xs text-indigo-200">
                                            What's the support level for ETH?
                                        </p>
                                    </div>
                                </div>
                                {/* Input Area */}
                                <div className="h-10 rounded-full bg-zinc-900 border border-white/10 flex items-center px-4">
                                    <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
                                    <span className="ml-3 text-xs text-zinc-600">AI is typing...</span>
                                </div>
                            </div>

                            {/* Content */}
                            <div className="mt-auto relative z-20 max-w-sm ml-auto text-right">
                                <div className="w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center mb-6 ml-auto">
                                    <MessageSquare className="w-6 h-6 text-indigo-400" />
                                </div>
                                <h3 className="text-2xl font-bold text-white mb-4">Your Personal Quant</h3>
                                <p className="text-zinc-400 text-sm mb-6">
                                    Not sure about a trade? Ask the AI Advisor. It has access to real-time market data, our strategy logic, and historical backtests.
                                </p>
                                <ul className="space-y-3 inline-block text-right">
                                    <li className="flex items-center gap-3 text-sm text-zinc-300 justify-end">
                                        <span className="font-medium text-white">Context-Aware Analysis</span> <Check className="w-4 h-4 text-emerald-500" />
                                    </li>
                                    <li className="flex items-center gap-3 text-sm text-zinc-300 justify-end">
                                        <span className="font-medium text-white">Risk Calculation Assistance</span> <Check className="w-4 h-4 text-emerald-500" />
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </SpotlightCard>

                </div>
            </div>
        </section>
    )
}
