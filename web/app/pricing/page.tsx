'use client'

import { Check, X, Sparkles, ArrowRight, Clock, MessageSquare, Bell, Zap, AlertTriangle, ShieldCheck, HelpCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ThemeToggle } from '@/components/theme-toggle'
import { cn } from '@/lib/utils'
import Link from 'next/link'
import { useUser } from '@/lib/user-context'
import { BrandLogo } from '@/components/brand-logo'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { billingService } from '@/services/billing'
import { toast } from 'sonner'
import { useState } from 'react'

// === COMPONENTS ===

function PricingBanner() {
  return (
    <div className="bg-gradient-to-r from-amber-500/10 via-amber-500/20 to-amber-500/10 border-b border-amber-500/20 backdrop-blur-md">
      <div className="container mx-auto px-4 py-2 flex items-center justify-center text-sm font-medium text-amber-500">
        <Sparkles className="h-4 w-4 mr-2 text-amber-500 fill-amber-500/20 animate-pulse" />
        Startup Offer: First 100 users lock in this price forever.
      </div>
    </div>
  )
}

interface PlanCardProps {
  name: string
  price: string
  period: string
  description: string
  features: { text: string; included: boolean; highlight?: boolean; tooltip?: string }[]
  cta: string
  href: string
  popular?: boolean
  isTrial?: boolean
  originalPrice?: string
  badge?: string
  onAction?: () => void
  isLoading?: boolean
}

function PlanCard({
  name,
  price,
  period,
  description,
  features,
  cta,
  href,
  popular = false,
  isTrial = false,
  originalPrice,
  badge,
  onAction,
  isLoading
}: PlanCardProps) {
  return (
    <Card
      className={cn(
        'relative flex flex-col transition-all duration-300',
        popular
          ? 'border-primary/50 shadow-2xl shadow-primary/10 bg-gradient-to-b from-card/80 to-primary/5'
          : 'bg-card/50 border-border/50 hover:border-border/80',
        isTrial && 'border-dashed border-border/60 bg-transparent'
      )}
    >
      {badge && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <Badge
            className={cn(
              "shadow-sm",
              popular ? "bg-primary text-primary-foreground" : "bg-amber-500 text-white hover:bg-amber-600"
            )}
          >
            {popular && <Sparkles className="h-3 w-3 mr-1 fill-current" />}
            {badge}
          </Badge>
        </div>
      )}

      <CardHeader className="text-center pb-2 pt-8">
        <CardTitle className="text-xl font-bold">{name}</CardTitle>
        <CardDescription className="text-muted-foreground min-h-[40px] flex items-center justify-center">
          {description}
        </CardDescription>
      </CardHeader>

      <CardContent className="flex flex-col flex-1 space-y-6">
        <div className="text-center py-4">
          <div className="flex items-center justify-center gap-2 items-end">
            {originalPrice && (
              <span className="text-lg text-muted-foreground/60 line-through decoration-muted-foreground/60 decoration-1 mb-1">
                {originalPrice}
              </span>
            )}
            <span className={cn("text-5xl font-bold tracking-tight", popular ? "text-primary" : "text-foreground")}>
              {price}
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-1 font-medium">{period}</p>
        </div>

        <div className="flex-1">
          <ul className="space-y-3">
            {features.map((feature) => (
              <li key={feature.text} className="flex items-start gap-3 group">
                {feature.included ? (
                  <div className={cn(
                    'rounded-full p-0.5 mt-0.5 shrink-0',
                    feature.highlight ? 'bg-primary/20 text-primary' : 'bg-primary/10 text-primary/70'
                  )}>
                    <Check className="h-3.5 w-3.5" />
                  </div>
                ) : (
                  <div className="rounded-full p-0.5 mt-0.5 shrink-0 bg-muted text-muted-foreground/40">
                    <X className="h-3.5 w-3.5" />
                  </div>
                )}
                <span
                  className={cn(
                    'text-sm leading-tight',
                    feature.included ? 'text-foreground/90' : 'text-muted-foreground/50'
                  )}
                >
                  {feature.text}
                </span>
              </li>
            ))}
          </ul>
        </div>

        <div className="mt-auto pt-6">
          {onAction ? (
            <Button
              className={cn(
                'w-full font-semibold',
                popular ? 'shadow-lg shadow-primary/20' : ''
              )}
              variant={popular ? 'default' : isTrial ? 'outline' : 'secondary'}
              size="lg"
              onClick={onAction}
              disabled={isLoading}
            >
              {isLoading ? "Redirecting..." : cta}
            </Button>
          ) : (
            <Link href={href} className="block w-full">
              <Button
                className={cn(
                  'w-full font-semibold',
                  popular ? 'shadow-lg shadow-primary/20' : ''
                )}
                variant={popular ? 'default' : isTrial ? 'outline' : 'secondary'}
                size="lg"
              >
                {cta}
              </Button>
            </Link>
          )}
          {originalPrice && (
            <p className="text-[10px] text-center text-muted-foreground mt-2 opacity-70">
              *Early adopter price locked forever
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

function FairUseSection() {
  return (
    <section className="mx-auto max-w-4xl mt-24 mb-16 px-4">
      <div className="rounded-2xl border border-border/40 bg-card/30 backdrop-blur-sm p-8">
        <div className="flex items-start gap-4">
          <div className="bg-blue-500/10 p-3 rounded-lg hidden sm:block">
            <ShieldCheck className="w-6 h-6 text-blue-500" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-semibold mb-2 flex items-center gap-2">
              Fair Use Policy (Swing Pro)
              <span className="sm:hidden bg-blue-500/10 p-1.5 rounded-md">
                <ShieldCheck className="w-4 h-4 text-blue-500" />
              </span>
            </h3>
            <p className="text-muted-foreground text-sm mb-6 leading-relaxed">
              To ensure platform stability and premium performance for all professionally active traders,
              we maintain generous but explicit limits on AI usage. Most users never hit these caps.
            </p>

            <div className="grid sm:grid-cols-2 gap-6">
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-foreground flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-primary" />
                  AI Advisor Chat
                </h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Unlimited inquiries allowed*</li>
                  <li>• Cap: 60 messages / day</li>
                  <li>• Cap: 1,200 messages / month</li>
                </ul>
              </div>

              <div className="space-y-2">
                <h4 className="text-sm font-medium text-foreground flex items-center gap-2">
                  <Zap className="w-4 h-4 text-amber-500" />
                  Pro Analyses (Deep Dives)
                </h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• 20 full analyses / day</li>
                  <li>• 300 analyses / month</li>
                  <li>• Rate limit: 20 requests / min</li>
                </ul>
              </div>
            </div>

            <p className="text-xs text-muted-foreground/60 mt-6 pt-4 border-t border-border/30">
              *Limits are enforced to prevent abuse. If you are a high-volume institutional user needing more capacity, please contact support.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}

function FAQSection() {
  const faqs = [
    {
      q: "What does 'Early Adopter' pricing mean?",
      a: "It means if you subscribe now, you secure the discounted price ($15 or $29) for the lifetime of your subscription. Even if we raise prices for new users later, your bill won't change."
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
    <section className="mx-auto max-w-3xl mt-16 mb-24 px-4">
      <h2 className="text-2xl font-bold text-center mb-8">Frequently Asked Questions</h2>
      <Accordion type="single" collapsible className="w-full">
        {faqs.map((faq, i) => (
          <AccordionItem key={i} value={`item-${i}`}>
            <AccordionTrigger className="text-left text-sm font-medium text-foreground/90">
              {faq.q}
            </AccordionTrigger>
            <AccordionContent className="text-muted-foreground leading-relaxed">
              {faq.a}
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </section>
  )
}

// === MAIN PAGE ===

export default function PricingPage() {
  const { user } = useUser()
  const [loadingPlan, setLoadingPlan] = useState<string | null>(null)

  const handleUpgrade = async (plan: string) => {
    try {
      if (!plan) return
      setLoadingPlan(plan)
      // Map plan name to backend enum
      const backendPlan = plan.includes("PRO") ? "PRO" : "TRADER"
      const { url } = await billingService.createCheckoutSession(backendPlan)
      if (url) {
        window.location.href = url
      }
    } catch (error) {
      console.error(error)
      toast.error("Failed to start checkout. Please try again.")
    } finally {
      setLoadingPlan(null)
    }
  }

  const plans = [
    {
      name: '3-Day Free Access',
      price: 'Free',
      period: '3 days free',
      description: 'Experience the edge risk-free.',
      badge: 'Risk Free',
      isTrial: true,
      features: [
        { text: 'Major Pairs (BTC, ETH)', included: true },
        { text: 'Real-time Telegram Alerts', included: true },
        { text: 'Professional Signal Scanning', included: true },
        { text: '4H & 1D Timeframes', included: true },
        { text: 'Basic Risk Engine', included: true },
        { text: 'Full Swing Lite Access', included: true },
        { text: 'AI Advisor Chat', included: false },
        { text: 'Institutional Analysis', included: false },
      ],
      cta: 'Start 3-Day Free Trial',
      href: '/auth/signup',
    },
    {
      name: 'Swing PRO',
      price: '$29',
      originalPrice: '$49',
      period: '/ month',
      badge: 'Best Value',
      popular: true,
      description: 'Professional grade with AI insights.',
      features: [
        { text: 'All Assets (BTC, ETH, SOL+)', included: true, highlight: true },
        { text: 'Real-time Telegram Alerts', included: true },
        { text: 'Unlimited Institutional Analysis', included: true, highlight: true },
        { text: '1H, 4H & 1D Timeframes', included: true },
        { text: 'AI Advisor Chat Access', included: true, highlight: true },
        { text: 'Smart Risk Engine', included: true },
        { text: 'Priority Support', included: true },
      ],
      cta: 'Get Swing PRO',
      href: '/auth/signup?plan=pro',
    },
    {
      name: 'Swing Lite',
      price: '$10',
      originalPrice: '$20',
      period: '/ month',
      description: 'Essential tools for active swing traders.',
      features: [
        { text: 'Major Pairs (BTC, ETH)', included: true, highlight: true },
        { text: 'Real-time Telegram Alerts', included: true, highlight: true },
        { text: 'Professional Signal Scanning', included: true },
        { text: '4H & 1D Timeframes', included: true },
        { text: 'Basic Risk Engine', included: true },
        { text: 'AI Advisor Chat', included: false },
        { text: 'Institutional Analysis', included: false },
      ],
      cta: 'Get Swing Lite',
      href: '/auth/signup?plan=trader',
    },
  ]

  // Inject upgrade handlers if user is logged in
  const displayPlans = plans.map(p => {
    // Skip handlers for free plan (signup link is fine, or maybe redirect to dashboard if logged in)
    if (user && p.isTrial) {
      return {
        ...p,
        cta: 'Go to Dashboard',
        href: '/dashboard',
        onAction: undefined
      }
    }

    if (user && !p.isTrial) {
      return {
        ...p,
        cta: user.plan === (p.name.includes("PRO") ? "PRO" : "TRADER") ? "Current Plan" : "Upgrade", // Simple check
        onAction: () => handleUpgrade(p.name),
        isLoading: loadingPlan === p.name
      }
    }
    return p
  })

  return (
    <div className="min-h-screen bg-background font-sans selection:bg-primary/20">
      {/* Dynamic Background */}
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/5 via-background to-background" />

      {/* Navbar */}
      <header className="sticky top-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-md">
        <PricingBanner />
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link href="/" className="block">
            <BrandLogo textSize="text-lg font-bold" />
          </Link>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            {user ? (
              <Link href="/dashboard">
                <Button size="sm">Go to Dashboard</Button>
              </Link>
            ) : (
              <>
                <Link href="/auth/login" className="hidden sm:block">
                  <Button variant="ghost" size="sm">Sign In</Button>
                </Link>
                <Link href="/auth/signup">
                  <Button size="sm">Get Started</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-20">

        {/* Hero Section */}
        <div className="text-center max-w-3xl mx-auto mb-20 space-y-6">
          <Badge variant="outline" className="border-primary/20 bg-primary/5 text-primary px-3 py-1 uppercase tracking-widest text-[10px] font-semibold">
            Limited Availability
          </Badge>
          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-foreground text-balance leading-tight">
            Institutional-Grade <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-amber-500">
              Market Intelligence.
            </span>
          </h1>
          <p className="text-lg text-muted-foreground text-pretty max-w-2xl mx-auto leading-relaxed">
            Stop trading on noise. Get <strong>precision swing signals</strong>, AI-validated risk scenarios, and real-time execution alerts.
            <br className="hidden sm:block" />
            <span className="text-foreground font-medium"> Professional tools for the retail trader.</span>
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid lg:grid-cols-3 gap-8 max-w-6xl mx-auto items-start">
          {displayPlans.map((plan) => (
            <PlanCard key={plan.name} {...plan} />
          ))}
        </div>

        {/* Fair Use Policy */}
        <FairUseSection />

        {/* Comparison or FAQ (Simplified to FAQ for conversions) */}
        <FAQSection />

        {/* Final CTA */}
        <div className="text-center py-12 border-t border-border/30">
          <h3 className="text-2xl font-bold mb-4">Ready to upgrade your trading?</h3>
          <p className="text-muted-foreground mb-8">Join the "Early Adopter" list before spots run out.</p>
          <Link href="/auth/signup">
            <Button size="lg" className="h-12 px-8 text-lg shadow-xl shadow-primary/20">
              Start 3-Day Free Trial
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          <p className="mt-4 text-xs text-muted-foreground">
            No credit card required for trial • Cancel anytime
          </p>
        </div>

      </main>

      {/* Footer */}
      <footer className="border-t border-border/40 py-12 bg-muted/5">
        <div className="container mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-6">
          <p className="text-xs text-muted-foreground">
            &copy; {new Date().getFullYear()} TraderCopilot Swing. All rights reserved.
          </p>
          <div className="flex gap-6 text-xs text-muted-foreground">
            <Link href="#" className="hover:text-foreground">Terms of Service</Link>
            <Link href="#" className="hover:text-foreground">Privacy Policy</Link>
            <Link href="#" className="hover:text-foreground">Fair Use Policy</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}

