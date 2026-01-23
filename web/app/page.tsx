'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import {
  ArrowRight,
  ChevronRight,
  TrendingUp,
  Shield,
  Zap,
  BarChart3,
  Terminal,
  Cpu,
  Globe,
  CheckCircle2,
  Lock,
  BrainCircuit,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ThemeToggle } from '@/components/theme-toggle'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/card'
import { BrandLogo } from '@/components/brand-logo'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'

// --- Visual Components ---

function HeroMockup() {
  return (
    <div className="relative mx-auto max-w-6xl w-full mt-16 px-4 sm:px-0 opacity-0 animate-fade-up delay-200" style={{ animationFillMode: 'forwards' }}>
      {/* Background Ambience */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-gradient-to-br from-emerald-500/10 via-indigo-500/5 to-transparent blur-[120px] -z-10" />

      {/* Main Container - The "Macbook" or "Browser" Window */}
      <div className="relative rounded-xl md:rounded-2xl border border-white/10 bg-[#09090b] shadow-[0_0_50px_-12px_rgba(0,0,0,0.8)] overflow-hidden ring-1 ring-white/5 group">

        {/* Browser Chrome / Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-white/5 bg-white/[0.02] backdrop-blur-md z-20 relative">
          <div className="flex items-center gap-2">
            <div className="flex gap-1.5 mr-4">
              <div className="w-3 h-3 rounded-full bg-[#FF5F56]/80 hover:bg-[#FF5F56] transition-colors" />
              <div className="w-3 h-3 rounded-full bg-[#FFBD2E]/80 hover:bg-[#FFBD2E] transition-colors" />
              <div className="w-3 h-3 rounded-full bg-[#27C93F]/80 hover:bg-[#27C93F] transition-colors" />
            </div>
            {/* Breadcrumbs */}
            <div className="hidden md:flex items-center gap-2 text-xs font-mono text-zinc-500">
              <Terminal className="w-3 h-3" />
              <span>tradercopilot.com</span>
              <span className="text-zinc-700">/</span>
              <span className="text-emerald-500">dashboard</span>
            </div>
          </div>

          {/* Status Indicator */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-wider">Live</span>
            </div>
          </div>
        </div>

        {/* App Layout */}
        <div className="grid md:grid-cols-[240px_1fr] h-[500px] md:h-[650px] overflow-hidden bg-[#09090b]">

          {/* Sidebar */}
          <div className="hidden md:flex flex-col border-r border-white/5 bg-zinc-900/20 pt-6">
            <div className="px-5 mb-8 flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-indigo-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <Terminal className="h-4 w-4 text-white" />
              </div>
              <div className="h-4 w-24 bg-zinc-800 rounded-md" />
            </div>

            <div className="space-y-1.5 px-3">
              {['Overview', 'Signals', 'Strategies', 'Advisor'].map((item, i) => (
                <div key={i} className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors",
                  i === 1 ? "bg-white/5 text-white" : "text-zinc-500"
                )}>
                  <div className={cn("h-4 w-4 rounded", i === 1 ? "bg-white/20" : "bg-zinc-800/50")} />
                  <span>{item}</span>
                  {i === 1 && <div className="ml-auto text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-500 text-black">2</div>}
                </div>
              ))}
            </div>

            <div className="mt-auto p-4 border-t border-white/5">
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-zinc-700 to-zinc-900 border border-white/10" />
                <div>
                  <div className="h-3 w-20 bg-zinc-800 rounded mb-1" />
                  <div className="h-2 w-12 bg-zinc-900 rounded" />
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="relative p-6 md:p-8 overflow-hidden bg-[url('/grid-pattern.svg')] bg-[size:24px_24px] bg-fixed">
            {/* Gradient overlay for grid */}
            <div className="absolute inset-0 bg-gradient-to-b from-[#09090b] via-transparent to-[#09090b]/80 pointer-events-none" />

            {/* Top Bar */}
            <div className="relative flex justify-between items-center mb-8 z-10">
              <div>
                <h2 className="text-xl font-semibold text-white mb-1">Active Signals</h2>
                <p className="text-xs text-zinc-500">Real-time market scanning active...</p>
              </div>
              <div className="flex gap-2">
                <div className="h-9 px-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-2 text-emerald-500 text-xs font-mono">
                  <Shield className="w-3 h-3" />
                  RISK: CONSERVATIVE
                </div>
              </div>
            </div>

            {/* DASHBOARD CONTENT */}
            <div className="relative grid gap-6 md:grid-cols-12 z-10">

              {/* Live Signal Card - Highlighted */}
              <div className="md:col-span-7 p-6 rounded-2xl border border-emerald-500/30 bg-gradient-to-br from-emerald-950/20 to-black relative overflow-hidden group shadow-2xl shadow-emerald-900/10">
                <div className="absolute top-0 right-0 p-4">
                  <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse box-shadow-glow" />
                </div>

                {/* Token Info */}
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-full bg-[#F7931A] flex items-center justify-center text-white font-bold text-lg shadow-lg">B</div>
                  <div>
                    <div className="text-lg font-bold text-white flex items-center gap-2">
                      BTC / USDT <span className="text-[10px] bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded border border-white/5">PERP</span>
                    </div>
                    <div className="text-sm text-emerald-400 font-mono mt-0.5">$97,245.50</div>
                  </div>
                  <div className="ml-auto pr-8 hidden sm:block">
                    <div className="text-right text-xs text-zinc-500 mb-1">24h Change</div>
                    <div className="text-right font-mono text-emerald-500">+4.2%</div>
                  </div>
                </div>

                {/* Trade Parameters */}
                <div className="grid grid-cols-3 gap-2 mb-6">
                  <div className="p-3 rounded-lg bg-zinc-900/50 border border-white/5">
                    <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">Entry Zone</div>
                    <div className="font-mono text-sm text-white">$96.8k - $97.2k</div>
                  </div>
                  <div className="p-3 rounded-lg bg-zinc-900/50 border border-white/5">
                    <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">Target</div>
                    <div className="font-mono text-sm text-emerald-400 font-bold">$105,000</div>
                  </div>
                  <div className="p-3 rounded-lg bg-zinc-900/50 border border-white/5">
                    <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">Stop</div>
                    <div className="font-mono text-sm text-red-400">$94,200</div>
                  </div>
                </div>

                {/* Mini Chart Visualization */}
                <div className="h-32 w-full flex items-end justify-between gap-1 opacity-80 pl-1">
                  {[40, 45, 42, 50, 55, 52, 58, 65, 60, 70, 75, 80, 95, 90, 85, 92, 98].map((h, i) => (
                    <div key={i} className={cn("w-full rounded-sm transition-all duration-500", i > 12 ? "bg-emerald-500" : "bg-emerald-500/20")} style={{ height: `${h}%` }} />
                  ))}
                </div>
              </div>

              {/* Side Cards */}
              <div className="md:col-span-5 space-y-4">
                {/* Advisor Card */}
                <div className="p-5 rounded-2xl border border-white/5 bg-zinc-900/30 backdrop-blur-sm">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="h-8 w-8 rounded-lg bg-indigo-500/10 flex items-center justify-center">
                      <Zap className="h-4 w-4 text-indigo-400" />
                    </div>
                    <span className="text-sm font-medium text-white">AI Analysis</span>
                  </div>
                  <p className="text-xs text-zinc-400 leading-relaxed">
                    <span className="text-indigo-400 font-semibold">@Advisor:</span> Bitcoin is showing a strong bullish divergence on the 4H RSI. Volume is increasing on spot exchanges. Recommended leverage: 3x.
                  </p>
                </div>

                {/* Watchlist Item */}
                <div className="p-4 rounded-xl border border-white/5 bg-zinc-900/20 flex items-center justify-between opacity-60 hover:opacity-100 transition-opacity">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-500/20 text-blue-500 flex items-center justify-center font-bold text-xs">E</div>
                    <div>
                      <div className="text-sm font-medium text-white">ETH/USDT</div>
                      <div className="text-[10px] text-zinc-500">Waiting for setup...</div>
                    </div>
                  </div>
                  <div className="text-xs font-mono text-zinc-400">$2,450</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Reflection Overlay */}
        <div className="absolute inset-0 bg-gradient-to-tr from-white/5 to-transparent pointer-events-none z-30" />
      </div>
    </div>
  )
}

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
    <div className={cn(
      "relative rounded-3xl p-8 flex flex-col transition-transform hover:-translate-y-1 duration-300",
      recommended
        ? "bg-zinc-900/80 border border-emerald-500/50 shadow-2xl shadow-emerald-500/10 backdrop-blur-md"
        : "bg-black/40 border border-white/10 backdrop-blur-sm"
    )}>
      {recommended && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2">
          <div className="px-4 py-1 bg-emerald-500 text-black text-xs font-bold uppercase tracking-wider rounded-full shadow-lg flex items-center gap-1.5">
            <Zap className="w-3 h-3 fill-black" />
            Most Popular
          </div>
        </div>
      )}

      {badge && !recommended && (
        <div className="absolute -top-3 left-8 px-3 py-1 bg-zinc-800 border border-white/10 text-white text-[10px] font-medium uppercase tracking-wider rounded-full shadow-lg">
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
          variant={recommended ? "default" : "outline"}
          className={cn(
            "w-full rounded-xl font-semibold h-12 transition-all",
            recommended
              ? "bg-emerald-500 hover:bg-emerald-400 text-black shadow-[0_0_20px_-5px_rgba(16,185,129,0.4)]"
              : "border-white/10 hover:bg-white/5 text-white hover:border-white/20"
          )}
        >
          {cta}
        </Button>
      </Link>
    </div>
  )
}

// --- Main Page ---

export default function HomePage() {
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="min-h-screen bg-black text-foreground selection:bg-emerald-500/30 selection:text-emerald-100 font-sans">

      {/* Background Gradients */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-500/5 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-emerald-500/5 blur-[120px]" />
        <div className="absolute top-[20%] left-[50%] -translate-x-1/2 w-[60%] h-[60%] rounded-full bg-primary/3 blur-[100px]" />
        <div className="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]" />
      </div>

      {/* Header */}
      <header
        className={cn(
          'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
          isScrolled ? 'bg-black/80 backdrop-blur-xl border-b border-white/10' : 'bg-transparent'
        )}
      >
        <div className="container mx-auto flex h-16 items-center justify-between px-4 lg:px-8">
          <Link href="/" className="block">
            <BrandLogo textSize="text-sm text-white" />
          </Link>

          <nav className="hidden md:flex items-center gap-6">
            {['Features', 'Pricing', 'Resources'].map((item) => (
              <Link
                key={item}
                href={item === 'Pricing' ? '#pricing' : `/#${item.toLowerCase()}`}
                className="text-sm font-medium text-muted-foreground hover:text-white transition-colors"
              >
                {item}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <Link href="/auth/login" className="hidden sm:block">
              <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-white">
                Log in
              </Button>
            </Link>
            <Link href="/auth/signup">
              <Button size="sm" className="bg-white text-black hover:bg-white/90 font-medium rounded-full px-5">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="relative z-10">

        {/* Hero Section */}
        <section className="pt-32 pb-20 px-4 relative">
          <div className="container mx-auto max-w-6xl text-center">

            {/* Announcement Pill */}
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 mb-8 animate-fade-in hover:bg-white/10 transition-colors cursor-default">
              <span className="flex h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-medium text-white/80">System Online v2.0</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-6 text-balance leading-[1.1]">
              Institutional Intelligence
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">
                For Retail Traders
              </span>
            </h1>

            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
              Stop guessing. Start executing.
              <br className="hidden sm:block" />
              TraderCopilot delivers high-probability swing setups directly to your dashboard.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20">
              <Link href="/auth/signup">
                <Button size="lg" className="h-12 px-8 text-base bg-emerald-500 hover:bg-emerald-600 text-black font-semibold rounded-full shadow-[0_0_20px_-5px_rgba(16,185,129,0.4)] hover:shadow-[0_0_30px_-5px_rgba(16,185,129,0.6)] transition-all">
                  Start Free Trial <ChevronRight className="ml-1 h-4 w-4" />
                </Button>
              </Link>
              <Link href="#features">
                <Button size="lg" variant="outline" className="h-12 px-8 text-base rounded-full border-white/10 bg-transparent hover:bg-white/5 text-white">
                  Explore Features
                </Button>
              </Link>
            </div>

            {/* The "Wow" Mockup */}
            <HeroMockup />

          </div>
        </section>

        {/* Feature Grid - "Bento" Style */}
        <section id="features" className="py-24 px-4 bg-zinc-950/50">
          <div className="container mx-auto max-w-6xl">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-white mb-4">Engineered for Precision</h2>
              <p className="text-muted-foreground">Automated analysis. Human execution.</p>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              {/* Large Card */}
              <div className="md:col-span-2 rounded-3xl border border-white/10 bg-zinc-900/20 p-8 relative overflow-hidden group hover:border-emerald-500/30 transition-colors">
                <div className="absolute top-0 right-0 p-12 bg-gradient-to-bl from-emerald-500/10 to-transparent rounded-bl-full pointer-events-none" />

                <div className="relative z-10">
                  <div className="h-12 w-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center mb-6">
                    <Cpu className="h-6 w-6 text-emerald-500" />
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-3">Algorithmic Detection</h3>
                  <p className="text-muted-foreground leading-relaxed max-w-md">
                    Our engine scans top cryptocurrencies 24/7 using institutional-grade technical models.
                    It identifies breakouts, trend reversals, and volatility contractions before they happen.
                  </p>
                </div>
              </div>

              {/* Tall Card */}
              <div className="md:row-span-2 rounded-3xl border border-white/10 bg-zinc-900/20 p-8 relative overflow-hidden group hover:border-indigo-500/30 transition-colors">
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-indigo-500/5 group-hover:to-indigo-500/10 transition-colors" />
                <div className="h-12 w-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center mb-6">
                  <Globe className="h-6 w-6 text-indigo-500" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">Global Markets</h3>
                <p className="text-muted-foreground mb-6">
                  While focused on Crypto (BTC, ETH, SOL), our models are calibrated for high-volatility global assets.
                </p>

                <div className="mt-auto space-y-3 relative z-10">
                  {['Bitcoin', 'Ethereum', 'Solana', 'BNB', 'XRP'].map((asset) => (
                    <div key={asset} className="flex items-center gap-3 p-3 rounded-xl bg-black/40 border border-white/5">
                      <div className="w-2 h-2 rounded-full bg-indigo-500/50" />
                      <span className="text-sm font-medium text-white/90">{asset}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Small Card 1 - AI Advisor */}
              <div className="rounded-3xl border border-white/10 bg-zinc-900/20 p-8 hover:bg-zinc-900/40 transition-colors group">
                <BrainCircuit className="h-8 w-8 text-violet-400 mb-4 group-hover:text-violet-300 transition-colors" />
                <h3 className="text-lg font-bold text-white mb-2">Personal AI Analyst</h3>
                <p className="text-sm text-muted-foreground">
                  Your own quantitative assistant. Ask questions, validate setups, and get real-time strategy insights on any asset.
                </p>
              </div>

              {/* Small Card 2 - Risk */}
              <div className="rounded-3xl border border-white/10 bg-zinc-900/20 p-8 hover:bg-zinc-900/40 transition-colors group">
                <Shield className="h-8 w-8 text-cyan-500 mb-4 group-hover:text-cyan-400 transition-colors" />
                <h3 className="text-lg font-bold text-white mb-2">Institutional Grade Risk</h3>
                <p className="text-sm text-muted-foreground">
                  Automated position sizing and invalidation logic built into every signal. Protect capital like a hedge fund.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing Section */}
        <section id="pricing" className="py-24 px-4 relative overflow-hidden">
          <div className="container mx-auto max-w-6xl relative z-10">
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

        {/* Social Proof / Justification */}
        <section className="py-24 px-4 bg-white/[0.02] border-t border-white/5">
          <div className="container mx-auto max-w-4xl text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-12">Why Traders Choose Copilot</h2>

            <div className="grid md:grid-cols-3 gap-8 divide-x-0 md:divide-x divide-white/5">
              <div className="p-6">
                <div className="text-4xl font-bold text-emerald-400 mb-2">24/7</div>
                <div className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Market Coverage</div>
              </div>
              <div className="p-6">
                <div className="text-4xl font-bold text-white mb-2">No Noise</div>
                <div className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Filtered Setups Only</div>
              </div>
              <div className="p-6">
                <div className="text-4xl font-bold text-cyan-400 mb-2">100%</div>
                <div className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Transparent History</div>
              </div>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <FAQSection />

        {/* CTA Footer */}
        <section className="py-32 px-4 relative overflow-hidden">
          <div className="absolute inset-0 bg-emerald-900/5" />
          <div className="container mx-auto max-w-4xl text-center relative z-10">
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">Ready to upgrade your trading?</h2>
            <p className="text-xl text-muted-foreground mb-10 max-w-xl mx-auto">
              Join the elite circle of traders using data, not emotion.
            </p>

            <Link href="/auth/signup">
              <Button size="lg" className="h-20 px-16 text-2xl bg-white text-black hover:bg-white rounded-full font-bold shadow-[0_0_40px_-10px_rgba(255,255,255,0.4)] hover:shadow-[0_0_80px_0px_rgba(255,255,255,0.9)] hover:scale-105 transition-all duration-500 ease-out">
                Start Your 3-Day Trial
              </Button>
            </Link>

            <div className="mt-8 flex justify-center gap-8 text-sm text-muted-foreground">
              <span className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-500" /> No credit card required</span>
              <span className="flex items-center gap-2"><Zap className="h-4 w-4 text-emerald-500" /> Instant Access</span>
            </div>
          </div>
        </section>

      </main>

      {/* Modern Footer */}
      <footer className="border-t border-white/10 bg-black py-12 px-4">
        <div className="container mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2 text-white/50">
            <Terminal className="h-5 w-5" />
            <span className="font-semibold text-white/80">TraderCopilot Swing</span>
          </div>
          <div className="text-sm text-white/40">
            © 2025 TraderCopilot. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}

function FAQSection() {
  const faqs = [
    {
      q: "What does 'Free Access' mean?",
      a: "It gives you full access to Swing Lite for 3 days. You can see live signals, use the scanner, and experience the platform. No credit card required."
    },
    {
      q: "Can I upgrade or downgrade later?",
      a: "Yes. You can upgrade from Lite to Pro or downgrade at any time. Changes take effect at the start of the next billing cycle."
    },
    {
      q: "What happens after the 3-day trial?",
      a: "If you don't upgrade, your account reverts to a limited state where you can no longer see live signals. You will not be charged unless you choose to subscribe."
    },
    {
      q: "What is the difference between Lite and Pro?",
      a: "Lite is great for following signals on major tokens. Pro gives you the AI Advisor to ask questions ('Why did we enter here?'), 1H timeframe signals for faster entries, and deeper 90-day history."
    }
  ]

  return (
    <section className="mx-auto max-w-3xl mt-16 mb-24 px-4 scroll-mt-24" id="faq">
      <h2 className="text-3xl font-bold text-center text-white mb-12">Frequently Asked Questions</h2>
      <Accordion type="single" collapsible className="w-full">
        {faqs.map((faq, i) => (
          <AccordionItem key={i} value={`item-${i}`} className="border-white/10">
            <AccordionTrigger className="text-left text-base font-medium text-white/90 hover:text-emerald-400 hover:no-underline py-6">
              {faq.q}
            </AccordionTrigger>
            <AccordionContent className="text-muted-foreground leading-relaxed text-base pb-6">
              {faq.a}
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </section>
  )
}
