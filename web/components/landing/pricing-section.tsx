'use client'

import Link from 'next/link'
import { Badge } from '@/components/ui/badge'
import { CheckCircle2, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { SpotlightCard } from '@/components/ui/spotlight-card'

function PricingCard({
    tier,
    price,
    originalPrice,
    features,
    recommended = false,
    cta = "Start Free Trial",
    href = "/auth/signup",
    badge
}: {
    tier: string,
    price: string,
    originalPrice?: string,
    features: string[],
    recommended?: boolean,
    cta?: string,
    href: string,
    badge?: string
}) {
    return (
        <SpotlightCard
            className={cn(
                "h-full transition-transform hover:-translate-y-1 duration-300",
                recommended ? "bg-zinc-900/60" : "bg-black/60"
            )}
            spotlightColor={recommended ? "rgba(16, 185, 129, 0.2)" : "rgba(255, 255, 255, 0.08)"}
        >
            <div className={cn(
                "p-8 h-full flex flex-col relative z-20",
                recommended ? "border-emerald-500/30" : "border-white/5"
            )}>
                {recommended && (
                    <div className="absolute -top-5 left-1/2 -translate-x-1/2 w-full flex justify-center">
                        <div className="px-4 py-1.5 bg-gradient-to-r from-emerald-500 to-emerald-400 text-black text-[11px] font-bold uppercase tracking-widest rounded-full shadow-[0_0_20px_-5px_rgba(16,185,129,0.8)] flex items-center gap-1.5 border border-emerald-300/50">
                            <Zap className="w-3.5 h-3.5 fill-black" />
                            Most Popular
                        </div>
                    </div>
                )}

                {badge && !recommended && (
                    <div className="absolute top-6 right-6 z-50 px-4 py-1.5 bg-white text-black text-xs font-extrabold uppercase tracking-widest rounded-full shadow-lg border border-white/20 transform hover:scale-105 transition-transform">
                        {badge}
                    </div>
                )}

                <div className="mb-8">
                    <h3 className={cn("text-lg font-bold mb-2", recommended ? "text-emerald-400" : "text-zinc-200")}>{tier}</h3>
                    <div className="flex items-end gap-2 mb-1">
                        <span className="text-4xl font-bold text-white">{price}</span>
                        {originalPrice && (
                            <span className="text-lg text-zinc-600 line-through decoration-zinc-600 decoration-1">{originalPrice}</span>
                        )}
                        {price !== 'Free' && <span className="text-sm text-zinc-500 mb-1.5">/mo</span>}
                    </div>
                    {originalPrice && (
                        <p className="text-xs text-emerald-500 font-medium">Early Adopter Price active</p>
                    )}
                </div>

                <div className="flex-1 space-y-4 mb-8">
                    {features.map((feat) => (
                        <div key={feat} className="flex items-start gap-3 text-sm text-zinc-300">
                            <CheckCircle2 className={cn("w-5 h-5 shrink-0", recommended ? "text-emerald-500" : "text-zinc-600")} />
                            <span className={recommended ? "text-white/90" : "text-zinc-400"}>{feat}</span>
                        </div>
                    ))}
                </div>

                <Link href={href} className="w-full">
                    <Button
                        size="lg"
                        className={cn(
                            "w-full rounded-xl font-bold h-12 transition-all",
                            recommended
                                ? "bg-emerald-500 hover:bg-emerald-400 text-black shadow-[0_0_20px_-5px_rgba(16,185,129,0.4)]"
                                : "bg-white text-black hover:bg-zinc-200 border-0"
                        )}
                    >
                        {cta}
                    </Button>
                </Link>
            </div>
        </SpotlightCard>
    )
}

export function PricingSection() {
    return (
        <section id="pricing" className="py-24 px-4 relative overflow-hidden">
            <div className="container mx-auto max-w-7xl relative z-10">
                <div className="text-center mb-16">
                    <Badge variant="outline" className="mb-4 px-3 py-1 bg-emerald-500/10 text-emerald-500 border-emerald-500/20">
                        Transparent Pricing
                    </Badge>
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Choose Your Edge</h2>
                    <p className="text-muted-foreground">Start for free. Upgrade when you're ready.</p>
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                    <PricingCard
                        tier="3-Day Free Access"
                        price="0$"
                        badge="Risk Free"
                        features={[
                            "Major Pairs (BTC, ETH)",
                            "Real-time Telegram Alerts",
                            "Professional Signal Scanning",
                            "4H & 1D Timeframes",
                            "Basic Risk Engine",
                            "Full Swing Lite Access"
                        ]}
                        href="/auth/signup"
                        cta="Start 3-Day Free Trial"
                    />

                    <PricingCard
                        tier="Swing PRO"
                        price="$29"
                        originalPrice="$49"
                        recommended={true}
                        features={[
                            "All Assets (BTC, ETH, SOL+)",
                            "Real-time Telegram Alerts",
                            "Unlimited Institutional Analysis",
                            "1H, 4H & 1D Timeframes",
                            "AI Advisor Chat Access",
                            "Smart Risk Engine",
                            "Priority Support"
                        ]}
                        href="/auth/signup?plan=pro"
                        cta="Get Swing PRO"
                    />

                    <PricingCard
                        tier="Swing Lite"
                        price="$10"
                        originalPrice="$20"
                        features={[
                            "Major Pairs (BTC, ETH)",
                            "Real-time Telegram Alerts",
                            "Professional Signal Scanning",
                            "4H & 1D Timeframes",
                            "Basic Risk Engine"
                        ]}
                        href="/auth/signup?plan=trader"
                        cta="Get Swing Lite"
                    />
                </div>
            </div>
        </section>
    )
}
