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
    <div className="flex h-[calc(100vh-8rem)] flex-col min-h-[500px]">
      <div className="mb-2 shrink-0">
        <h1 className="text-lg font-bold tracking-tight text-foreground">AI Advisor</h1>
        <p className="text-xs text-muted-foreground">Get personalized swing trading insights</p>
      </div>

      <Card className="flex flex-1 bg-card/50 border-border backdrop-blur-sm shadow-sm overflow-hidden">
        <CardContent className="flex flex-1 flex-col items-center justify-center p-4 lg:p-6">
          <div className="max-w-md w-full space-y-3 text-center">
            {/* Icon */}
            <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/20 shadow-sm shrink-0">
              <Lock className="h-5 w-5 text-primary" />
            </div>

            {/* Headline */}
            <div className="space-y-1 shrink-0">
              <h2 className="text-lg font-semibold tracking-tight text-foreground">
                Advisor is a SwingPro feature
              </h2>
              <p className="text-xs text-muted-foreground leading-normal max-w-sm mx-auto">
                Unlock AI-powered swing trading guidance via the most advanced plan.
              </p>
            </div>

            {/* Benefits */}
            <div className="grid gap-2 text-left shrink-0">
              {benefits.map((benefit) => (
                <div
                  key={benefit.title}
                  className="flex gap-2.5 p-2 rounded-md bg-secondary/30 border border-border/50 items-center"
                >
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded bg-primary/10 border border-primary/20">
                    <benefit.icon className="h-3.5 w-3.5 text-primary" />
                  </div>
                  <div className="">
                    <h3 className="font-semibold text-foreground text-xs">{benefit.title}</h3>
                    <p className="text-[10px] text-muted-foreground leading-tight line-clamp-1">
                      {benefit.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Pro Badge */}
            <div className="flex items-center justify-center gap-1.5 text-xs text-muted-foreground pt-1 shrink-0">
              <Sparkles className="h-3 w-3 text-primary" />
              <span className="text-[11px]">
                Included in <span className="font-bold text-primary">SwingPro</span> at <span className="line-through opacity-70 ml-0.5">$49</span> $29/mo
              </span>
            </div>

            {/* CTAs */}
            <div className="flex flex-row items-center justify-center gap-2 pt-1 shrink-0">
              <Link href="/pricing">
                <Button size="sm" className="gap-1.5 min-w-[140px] h-8 text-xs font-semibold shadow-md shadow-primary/10">
                  Upgrade to SwingPro
                  <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button size="sm" variant="ghost" className="gap-1.5 text-muted-foreground hover:text-foreground h-8 text-xs">
                  <ArrowLeft className="h-3.5 w-3.5" />
                  Back
                </Button>
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
