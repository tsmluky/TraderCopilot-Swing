'use client'

import { useState } from 'react'
import { Bell, MessageCircle, Lock, Check, Plus, Trash2 } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { useUser } from '@/lib/user-context'
import Link from 'next/link'

const alertTypes = [
  { id: 'new-signal', label: 'New Signal Alert', description: 'Get notified when a new trading signal is generated' },
  { id: 'target-hit', label: 'Target Price Hit', description: 'Alert when a signal reaches its target price' },
  { id: 'stop-loss', label: 'Stop Loss Triggered', description: 'Alert when a signal hits stop loss' },
  { id: 'daily-summary', label: 'Daily Summary', description: 'Receive a daily recap of all signals and performance' },
]

export default function AlertsPage() {
  const { user, canAccessTelegram } = useUser()
  const [alerts, setAlerts] = useState<Record<string, boolean>>({
    'new-signal': true,
    'target-hit': true,
    'stop-loss': true,
    'daily-summary': false,
  })

  const toggleAlert = (id: string) => {
    setAlerts((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Alert Settings</h1>
        <p className="text-muted-foreground">
          Configure how you receive trading notifications
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Telegram Integration */}
        <Card className="bg-card border-border">
          <CardHeader>
            <div className="flex items-center gap-2">
              <MessageCircle className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg">Telegram Notifications</CardTitle>
            </div>
            <CardDescription>
              Receive instant alerts directly to your Telegram
            </CardDescription>
          </CardHeader>
          <CardContent>
            {canAccessTelegram() ? (
              <div className="space-y-4">
                {user?.telegramConnected ? (
                  <div className="flex items-center justify-between rounded-lg bg-success/10 border border-success/20 p-4">
                    <div className="flex items-center gap-3">
                      <div className="rounded-full bg-success/20 p-2">
                        <Check className="h-4 w-4 text-success" />
                      </div>
                      <div>
                        <p className="font-medium text-foreground">Connected</p>
                        <p className="text-sm text-muted-foreground">@yourhandle</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      Disconnect
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="rounded-lg bg-secondary/30 p-4 space-y-3">
                      <p className="text-sm text-muted-foreground">
                        Connect your Telegram account to receive instant trading alerts
                      </p>
                      <ol className="text-sm text-muted-foreground space-y-2 list-decimal list-inside">
                        <li>Open Telegram and search for @TraderCopilotBot</li>
                        <li>Start a conversation and click /connect</li>
                        <li>Enter the code shown below</li>
                      </ol>
                      <div className="flex items-center gap-2">
                        <Input
                          value="TC-DEMO-7X9K2"
                          readOnly
                          className="font-mono bg-background"
                        />
                        <Button variant="outline" size="sm">
                          Copy
                        </Button>
                      </div>
                    </div>
                    <Button className="w-full">
                      Verify Connection
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <div className="rounded-full bg-muted p-3 mb-3">
                  <Lock className="h-6 w-6 text-muted-foreground" />
                </div>
                <p className="font-medium text-foreground mb-1">Telegram alerts are not available in Trial</p>
                <p className="text-sm text-muted-foreground mb-4">
                  Upgrade to SwingLite or SwingPro to unlock instant Telegram notifications
                </p>
                <Link href="/pricing">
                  <Button>View Plans</Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Alert Preferences */}
        <Card className="bg-card border-border">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg">Alert Preferences</CardTitle>
            </div>
            <CardDescription>
              Choose which notifications you want to receive
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {alertTypes.map((alert) => (
              <div
                key={alert.id}
                className="flex items-center justify-between rounded-lg bg-secondary/30 p-4"
              >
                <div className="space-y-0.5">
                  <Label htmlFor={alert.id} className="font-medium text-foreground cursor-pointer">
                    {alert.label}
                  </Label>
                  <p className="text-xs text-muted-foreground">{alert.description}</p>
                </div>
                <Switch
                  id={alert.id}
                  checked={alerts[alert.id]}
                  onCheckedChange={() => toggleAlert(alert.id)}
                  disabled={!canAccessTelegram() && alert.id !== 'daily-summary'}
                />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Price Alerts (Coming Soon) */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            Custom Price Alerts
            <Badge variant="secondary" className="text-xs">Coming Soon</Badge>
          </CardTitle>
          <CardDescription>
            Set custom price alerts for any supported token
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8 text-center">
            <div className="max-w-sm">
              <p className="text-muted-foreground mb-4">
                Custom price alerts are coming soon. You&apos;ll be able to set alerts for specific price levels on any token.
              </p>
              <Button variant="outline" disabled>
                <Plus className="h-4 w-4 mr-2" />
                Add Price Alert
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
