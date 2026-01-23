'use client'

import Link from 'next/link'
import { Lock, Clock, Brain, Target, ArrowRight, ArrowLeft, Sparkles } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

const benefits = [
  {
    icon: Clock,
    title: '1H Timeframe Access',
    description: 'Unlock the 1-hour chart for faster swing entries and tighter stop management.',
  },
  {
    icon: Brain,
    title: 'LLM Swing Analysis',
    description: 'Get AI-powered market analysis, sentiment readings, and setup evaluations in real-time.',
  },
  {
    icon: Target,
    title: 'Position Management',
    description: 'Receive guidance on entries, exits, partial takes, and risk adjustments for active trades.',
  },
]

export function AdvisorLocked() {
  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">AI Advisor</h1>
        <p className="text-muted-foreground">Get personalized swing trading insights</p>
      </div>

      <Card className="flex flex-1 bg-card/50 border-border backdrop-blur-sm">
        <CardContent className="flex flex-1 flex-col items-center justify-center p-8 lg:p-12">
          <div className="max-w-lg w-full space-y-8 text-center">
            {/* Icon */}
            <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/20">
              <Lock className="h-9 w-9 text-primary" />
            </div>

            {/* Headline */}
            <div className="space-y-3">
              <h2 className="text-2xl font-semibold tracking-tight text-foreground">
                Advisor is a SwingPro feature
              </h2>
              <p className="text-muted-foreground leading-relaxed max-w-md mx-auto">
                Unlock AI-powered swing trading guidance with our most advanced plan. 
                Get real-time analysis and position management support.
              </p>
            </div>

            {/* Benefits */}
            <div className="grid gap-4 text-left">
              {benefits.map((benefit) => (
                <div
                  key={benefit.title}
                  className="flex gap-4 p-4 rounded-xl bg-secondary/30 border border-border/50"
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 border border-primary/20">
                    <benefit.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div className="space-y-1">
                    <h3 className="font-medium text-foreground text-sm">{benefit.title}</h3>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      {benefit.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Pro Badge */}
            <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <Sparkles className="h-4 w-4 text-primary" />
              <span>
                Included in <span className="font-medium text-primary">SwingPro</span> at $99/month
              </span>
            </div>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link href="/pricing">
                <Button size="lg" className="gap-2 min-w-[200px]">
                  Upgrade to SwingPro
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button size="lg" variant="ghost" className="gap-2 text-muted-foreground hover:text-foreground">
                  <ArrowLeft className="h-4 w-4" />
                  Back to Dashboard
                </Button>
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
