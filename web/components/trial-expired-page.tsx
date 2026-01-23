'use client'

import { Clock, ArrowRight, Send, Bot, X, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'

const trialFeatures = [
  { feature: 'BTC & ETH signals', included: true },
  { feature: '4H & 1D timeframes', included: true },
  { feature: 'Signal evaluation', included: true },
  { feature: 'Telegram alerts', included: false },
  { feature: '1H timeframe', included: false },
  { feature: 'AI Advisor chat', included: false },
]

const plans = [
  {
    name: 'SwingLite',
    price: 49,
    description: 'Essential swing signals with Telegram delivery',
    badge: null,
    features: [
      'All 5 tokens (BTC, ETH, SOL, BNB, XRP)',
      '4H & 1D timeframes',
      'Telegram alerts',
      'Signal evaluation & history',
    ],
    cta: 'Upgrade to SwingLite',
    href: '/pricing?plan=lite',
    variant: 'outline' as const,
  },
  {
    name: 'SwingPro',
    price: 99,
    description: 'Full access with AI-powered insights',
    badge: 'Most Popular',
    features: [
      'Everything in SwingLite',
      '1H timeframe access',
      'AI Advisor chat',
      'Priority signal delivery',
    ],
    cta: 'Upgrade to SwingPro',
    href: '/pricing?plan=pro',
    variant: 'default' as const,
  },
]

export function TrialExpiredPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-6">
      <div className="w-full max-w-4xl space-y-10">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-muted/50 border border-border">
            <Clock className="h-8 w-8 text-muted-foreground" />
          </div>

          <div className="space-y-2">
            <h1 className="text-3xl font-bold tracking-tight text-foreground">
              Your 3-day trial has ended
            </h1>
            <p className="text-muted-foreground max-w-lg mx-auto">
              Upgrade to keep receiving swing signals and unlock Telegram alerts and AI Advisor.
            </p>
          </div>
        </div>

        {/* Upgrade Cards */}
        <div className="grid gap-6 md:grid-cols-2">
          {plans.map((plan) => (
            <Card
              key={plan.name}
              className={`relative bg-card/50 border-border transition-all hover:border-primary/50 ${plan.badge ? 'ring-1 ring-primary/20' : ''
                }`}
            >
              {plan.badge && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="bg-primary text-primary-foreground">
                    {plan.badge}
                  </Badge>
                </div>
              )}

              <CardHeader className="pb-4">
                <div className="flex items-baseline justify-between">
                  <CardTitle className="text-xl">{plan.name}</CardTitle>
                  <div className="text-right">
                    <span className="text-3xl font-bold">${plan.price}</span>
                    <span className="text-muted-foreground text-sm">/mo</span>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">{plan.description}</p>
              </CardHeader>

              <CardContent className="space-y-6">
                <ul className="space-y-3">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3 text-sm">
                      <Check className="h-4 w-4 text-primary mt-0.5 shrink-0" />
                      <span className="text-foreground">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link href={plan.href} className="block">
                  <Button
                    variant={plan.variant}
                    className={`w-full gap-2 ${plan.variant === 'outline' ? 'bg-transparent' : ''}`}
                  >
                    {plan.cta}
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Trial Recap */}
        <Card className="bg-muted/30 border-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-base font-medium text-muted-foreground">
              What you had during your trial
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-6">
              {trialFeatures.map((item) => (
                <div
                  key={item.feature}
                  className="flex items-center gap-2 text-sm"
                >
                  {item.included ? (
                    <Check className="h-4 w-4 text-primary shrink-0" />
                  ) : (
                    <X className="h-4 w-4 text-muted-foreground/50 shrink-0" />
                  )}
                  <span className={item.included ? 'text-foreground' : 'text-muted-foreground/50'}>
                    {item.feature}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Upgrade Benefits */}
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="flex items-start gap-4 p-4 rounded-lg bg-card/30 border border-border">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
              <Send className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="font-medium text-foreground">Telegram Alerts</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Get signals delivered instantly to Telegram so you never miss an entry.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4 p-4 rounded-lg bg-card/30 border border-border">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
              <Bot className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="font-medium text-foreground">AI Advisor</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Chat with our LLM for swing analysis and position management guidance.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center space-y-4">
          <Link href="/dashboard">
            <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
              Return to Dashboard
            </Button>
          </Link>

          <p className="text-xs text-muted-foreground">
            Questions? Contact{' '}
            <a href="mailto:support@tradercopilot.io" className="text-primary hover:underline">
              support@tradercopilot.io
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
