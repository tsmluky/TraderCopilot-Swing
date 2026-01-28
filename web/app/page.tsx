import Link from 'next/link'
import { ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { StrategyShowcase } from '@/components/landing/strategy-showcase'
import { PremiumFeatures } from '@/components/landing/premium-features'
import { SiteHeader } from '@/components/landing/site-header'
import { HeroMockup } from '@/components/landing/hero-mockup'
import { PricingSection } from '@/components/landing/pricing-section'
import { FAQSection } from '@/components/landing/faq-section'
import { TransparencyHub } from '@/components/landing/transparency-hub'
import { CopilotFeatures } from '@/components/landing/copilot-features'

export const metadata = {
  title: 'TraderCopilot Swing | Institutional Intelligence for Retail',
  description: 'Automated swing trading setups with verifiable 5-year backtests. Stop guessing and start executing with precision.',
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-black text-foreground selection:bg-emerald-500/30 selection:text-emerald-100 font-sans">

      {/* Background Gradients */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-500/5 blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-emerald-500/5 blur-[120px]" />
        <div className="absolute top-[20%] left-[50%] -translate-x-1/2 w-[60%] h-[60%] rounded-full bg-primary/3 blur-[100px]" />
        <div className="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]" />
      </div>

      {/* Client-Side Header (Scroll effect) */}
      <SiteHeader />

      <main className="relative z-10">

        {/* Global Ambient Background (Fixed) */}
        {/* Global Ambient Background (Fixed) */}
        <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-black to-black pointer-events-none -z-50" />
        <div className="fixed inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none -z-50" />
        <div className="fixed inset-0 bg-[url('/noise.png')] opacity-[0.03] mix-blend-overlay pointer-events-none -z-50" />

        {/* Hero Section - Full Height */}
        <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden pt-20">

          {/* Local Hero Auroras */}
          <div className="absolute top-[-10%] left-1/2 -translate-x-1/2 w-[140%] h-[1000px] bg-gradient-to-b from-indigo-500/10 via-emerald-500/5 to-transparent opacity-60 blur-[100px] pointer-events-none" />

          <div className="container mx-auto max-w-full px-4 text-center relative z-10 flex flex-col items-center">

            {/* Announcement Pill */}
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 mb-8 animate-fade-in hover:bg-white/10 transition-colors cursor-default backdrop-blur-sm">
              <span className="flex h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-medium text-white/80 tracking-wide">SYSTEM V2.0 ONLINE</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-8 text-balance leading-[1.1]">
              Institutional Intelligence
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-cyan-400 to-indigo-400 animate-gradient-x">
                For Retail Traders
              </span>
            </h1>

            <p className="text-lg md:text-xl text-zinc-400 max-w-3xl mx-auto mb-10 leading-relaxed font-light">
              Stop guessing based on gut feeling. Start executing with <span className="text-emerald-400 font-medium">mathematical precision</span>.
              <br className="hidden sm:block" />
              Our engines scan <span className="text-white">major liquid pairs</span> continuously, filtering noise to deliver high-probability swing setups directly to your execution terminal.
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

        {/* Strategy Performance Showcase (The Engine) */}
        <StrategyShowcase />

        {/* Premium Features Grid (The "Surprise") */}
        <PremiumFeatures />

        {/* Transparency / Audit Hub */}
        <TransparencyHub />

        {/* AI Co-Pilot & Telegram */}
        <CopilotFeatures />

        {/* Pricing Section */}
        <PricingSection />

        {/* Social Proof / Trusted By */}
        <section className="py-20 border-t border-white/5">
          <div className="container mx-auto text-center">
            <p className="text-sm font-medium text-zinc-500 uppercase tracking-widest mb-8">Trusted by data feeds from</p>
            <div className="flex flex-wrap justify-center gap-12 opacity-50 grayscale hover:grayscale-0 transition-all duration-500">
              <span className="text-xl font-bold text-zinc-300">BINANCE</span>
              <span className="text-xl font-bold text-zinc-300">BYBIT</span>
              <span className="text-xl font-bold text-zinc-300">COINGECKO</span>
              <span className="text-xl font-bold text-zinc-300">TRADINGVIEW</span>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <FAQSection />

        {/* Footer */}
        <footer className="py-12 px-4 border-t border-white/5 bg-black">
          <div className="container mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="text-zinc-500 text-sm">
              © 2024 TraderCopilot Swing. All rights reserved.
            </div>
            <div className="flex gap-6 text-sm text-zinc-500">
              <Link href="#" className="hover:text-white transition-colors">Privacy Policy</Link>
              <Link href="#" className="hover:text-white transition-colors">Terms of Service</Link>
              <Link href="#" className="hover:text-white transition-colors">Contact</Link>
            </div>
          </div>
        </footer>

      </main>
    </div>
  )
}
