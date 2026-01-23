'use client'

import { Crown, Sparkles, Clock } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { useUser } from '@/lib/user-context'

export function PlanBadge() {
  const { user } = useUser()

  if (!user) return null

  const planConfig = {
    FREE: {
      label: 'Trial',
      icon: Clock,
      className: 'bg-amber-500/10 text-amber-500 border-amber-500/30 hover:bg-amber-500/20',
    },
    TRADER: {
      label: 'SwingLite',
      icon: Sparkles,
      className: 'bg-blue-500/10 text-blue-500 border-blue-500/30 hover:bg-blue-500/20',
    },
    PRO: {
      label: 'SwingPro',
      icon: Crown,
      className: 'bg-primary/10 text-primary border-primary/30 hover:bg-primary/20',
    },
  }

  const planKey = (user.plan || 'FREE').toUpperCase()
  const config = planConfig[planKey as keyof typeof planConfig] || planConfig.FREE
  const Icon = config.icon

  // Calculate trial days remaining
  const trialDaysLeft = user.plan === 'FREE' && user.trialExpiresAt
    ? Math.max(0, Math.ceil((user.trialExpiresAt.getTime() - Date.now()) / (1000 * 60 * 60 * 24)))
    : null

  return (
    <Badge variant="outline" className={cn('gap-1.5 px-2.5 py-1', config.className)}>
      <Icon className="h-3.5 w-3.5" />
      <span className="font-medium">{config.label}</span>
      {trialDaysLeft !== null && trialDaysLeft > 0 && (
        <span className="text-xs opacity-75">({trialDaysLeft}d left)</span>
      )}
    </Badge>
  )
}
