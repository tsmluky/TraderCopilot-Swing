'use client'

import React from "react"

import Link from 'next/link'
import { Lock, Crown, ArrowRight } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface LockedFeatureCardProps {
  title: string
  description: string
  requiredPlan: 'TRADER' | 'PRO'
  icon?: React.ReactNode
  className?: string
  fullScreen?: boolean
}

export function LockedFeatureCard({
  title,
  description,
  requiredPlan,
  icon,
  className,
  fullScreen = false,
}: LockedFeatureCardProps) {
  const planLabel = requiredPlan === 'PRO' ? 'SwingPro' : 'SwingLite'
  const planColor = requiredPlan === 'PRO' ? 'text-primary' : 'text-blue-500'
  
  if (fullScreen) {
    return (
      <div className={cn('flex flex-1 items-center justify-center min-h-[60vh]', className)}>
        <div className="text-center max-w-md mx-auto px-4">
          <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-muted/50 border border-border">
            {icon || <Lock className="h-10 w-10 text-muted-foreground" />}
          </div>
          <h2 className="text-2xl font-bold text-foreground mb-2">{title}</h2>
          <p className="text-muted-foreground mb-6">{description}</p>
          <div className="flex flex-col items-center gap-3">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Crown className={cn('h-4 w-4', planColor)} />
              <span>
                Requires <span className={cn('font-medium', planColor)}>{planLabel}</span> or higher
              </span>
            </div>
            <Link href="/pricing">
              <Button className="gap-2">
                Upgrade to {planLabel}
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    )
  }
  
  return (
    <Card className={cn('bg-card/50 border-border border-dashed', className)}>
      <CardContent className="flex flex-col items-center justify-center p-8 text-center min-h-[200px]">
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-muted/50 border border-border">
          {icon || <Lock className="h-6 w-6 text-muted-foreground" />}
        </div>
        <h3 className="font-semibold text-foreground mb-1">{title}</h3>
        <p className="text-sm text-muted-foreground mb-4 max-w-xs">{description}</p>
        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-3">
          <Crown className={cn('h-3.5 w-3.5', planColor)} />
          <span>Requires {planLabel}</span>
        </div>
        <Link href="/pricing">
          <Button size="sm" variant="outline" className="gap-1.5 bg-transparent">
            Upgrade
            <ArrowRight className="h-3.5 w-3.5" />
          </Button>
        </Link>
      </CardContent>
    </Card>
  )
}
