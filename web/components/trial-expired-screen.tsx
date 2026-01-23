'use client'

import { Clock, ArrowRight, Zap, Shield, MessageSquare } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import Link from 'next/link'

const features = [
  {
    icon: Zap,
    title: 'Real-time Signals',
    description: 'Get instant swing trading signals for BTC, ETH, SOL, BNB, and XRP',
  },
  {
    icon: Shield,
    title: 'Proven Strategies',
    description: 'Access battle-tested strategies with 65-74% win rates',
  },
  {
    icon: MessageSquare,
    title: 'AI Advisor',
    description: 'Get personalized swing trading insights with our LLM advisor (Pro)',
  },
]

export function TrialExpiredScreen() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-6">
      <div className="w-full max-w-2xl space-y-8 text-center">
        {/* Icon */}
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-destructive/10">
          <Clock className="h-10 w-10 text-destructive" />
        </div>

        {/* Title */}
        <div className="space-y-3">
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            Your Trial Has Expired
          </h1>
          <p className="text-lg text-muted-foreground">
            Your 3-day free trial has ended. Upgrade now to continue receiving
            professional swing trading signals and insights.
          </p>
        </div>

        {/* Features */}
        <div className="grid gap-4 sm:grid-cols-3">
          {features.map((feature) => (
            <Card key={feature.title} className="bg-card/50 border-border">
              <CardHeader className="pb-2">
                <feature.icon className="mx-auto h-8 w-8 text-primary" />
              </CardHeader>
              <CardContent className="text-center">
                <CardTitle className="text-sm font-medium">{feature.title}</CardTitle>
                <CardDescription className="mt-1 text-xs">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* CTA */}
        <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Link href="/pricing">
            <Button size="lg" className="w-full sm:w-auto gap-2">
              View Plans & Upgrade
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/">
            <Button size="lg" variant="outline" className="w-full sm:w-auto bg-transparent">
              Back to Home
            </Button>
          </Link>
        </div>

        {/* Support */}
        <p className="text-sm text-muted-foreground">
          Need help? Contact us at{' '}
          <a href="mailto:support@tradercopilot.io" className="text-primary hover:underline">
            support@tradercopilot.io
          </a>
        </p>
      </div>
    </div>
  )
}
