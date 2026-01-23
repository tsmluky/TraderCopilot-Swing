'use client'

import { Clock, Bell, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useUser } from '@/lib/user-context'
import Link from 'next/link'

export function QuickStats() {
  const { user, canAccessTelegram } = useUser()

  const trialDaysLeft = user?.trialExpiresAt
    ? Math.max(0, Math.ceil((user.trialExpiresAt.getTime() - Date.now()) / (1000 * 60 * 60 * 24)))
    : 0

  return (
    <div className="space-y-4">
      {/* Trial Banner (only for FREE users) */}
      {user?.plan === 'FREE' && (
        <Card className="bg-primary/5 border-primary/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="rounded-full bg-primary/10 p-2">
                  <Clock className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">Trial Period</p>
                  <p className="text-xs text-muted-foreground">
                    {trialDaysLeft} day{trialDaysLeft !== 1 ? 's' : ''} remaining
                  </p>
                </div>
              </div>
              <Link href="/pricing">
                <Button size="sm" className="h-8">
                  Upgrade Now
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Telegram Status */}
      <Card className="bg-card border-border">
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-medium flex items-center gap-2">
            <Bell className="h-4 w-4 text-primary" />
            Alert Notifications
          </CardTitle>
        </CardHeader>
        <CardContent>
          {canAccessTelegram() ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Telegram</span>
                <Badge
                  variant={user?.telegramConnected ? 'default' : 'secondary'}
                  className="text-xs"
                >
                  {user?.telegramConnected ? 'Connected' : 'Not Connected'}
                </Badge>
              </div>
              {!user?.telegramConnected && (
                <Button size="sm" variant="outline" className="w-full bg-transparent">
                  Connect Telegram
                </Button>
              )}
            </div>
          ) : (
            <div className="text-center py-2">
              <p className="text-sm text-muted-foreground mb-2">
                Telegram alerts require a paid plan
              </p>
              <Link href="/pricing">
                <Button size="sm" variant="outline" className="text-xs bg-transparent">
                  Upgrade to unlock
                </Button>
              </Link>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Performance */}
      <Card className="bg-card border-border">
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-medium flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-primary" />
            Recent Performance
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Last 7 days</span>
            <span className="font-medium text-success">+12.4%</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Last 30 days</span>
            <span className="font-medium text-success">+28.7%</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Signals this week</span>
            <span className="font-medium text-foreground">14</span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
