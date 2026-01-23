'use client'

import { useState, useEffect } from 'react'
import { User, Shield, CreditCard, Bell, Moon, Globe, Send, Lock } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useAuth } from '@/context/auth-context'
import { authService } from '@/services/auth'
import { toast } from 'sonner'
import Link from 'next/link'

export default function SettingsPage() {
  const { user, entitlements, refresh } = useAuth()

  // Initialize state directly from props if possible, or wait for effect
  const [timezone, setTimezone] = useState('UTC')
  const [newPassword, setNewPassword] = useState('')
  const [oldPassword, setOldPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    if (user?.timezone) {
      setTimezone(user.timezone)
    }
  }, [user])

  // Prevent hydration mismatch by rendering a safe fallback or null until mounted
  if (!mounted) {
    return <div className="p-6 space-y-6 animate-pulse">
      <div className="h-8 w-48 bg-secondary/50 rounded"></div>
      <div className="space-y-4">
        <div className="h-40 bg-card rounded border border-border/50"></div>
        <div className="h-40 bg-card rounded border border-border/50"></div>
      </div>
    </div>
  }

  const planLabel = entitlements?.plan_label || user?.plan || 'Free'

  const handleUpdateTimezone = async (val: string) => {
    try {
      setTimezone(val)
      await authService.updateTimezone(val)
      toast.success("Timezone updated")
      refresh()
    } catch (e) {
      console.error(e)
      toast.error("Failed to update timezone")
    }
  }

  const handleUpdatePassword = async () => {
    if (!newPassword || !oldPassword) return
    try {
      setIsLoading(true)
      await authService.updatePassword(oldPassword, newPassword)
      toast.success("Password updated successfully")
      setNewPassword('')
      setOldPassword('')
    } catch (e) {
      toast.error("Failed to update password")
    } finally {
      setIsLoading(false)
    }
  }

  // Handle manual disconnect
  const handleDisconnect = async () => {
    try {
      await authService.updateTelegram('')
      toast.success("Disconnected Telegram")
      refresh()
    } catch (e) {
      toast.error("Failed to disconnect")
    }
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Settings</h1>
        <p className="text-muted-foreground">
          Manage your account and preferences
        </p>
      </div>

      <div className="grid gap-6">
        {/* Profile Section */}
        <Card className="bg-card border-border">
          <CardHeader>
            <div className="flex items-center gap-2">
              <User className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg">Profile</CardTitle>
            </div>
            <CardDescription>Your personal information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <div className="flex">
                  <Input id="name" value={user?.name || ''} readOnly className="bg-muted/50 text-muted-foreground border-transparent focus-visible:ring-0" />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="flex">
                  <Input id="email" value={user?.email || ''} className="bg-muted/50 text-muted-foreground border-transparent focus-visible:ring-0" readOnly />
                </div>
              </div>

              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between sm:col-span-2 pt-4 border-t border-border/50 mt-2">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <Label className="text-base font-medium">Telegram Notifications</Label>
                    {user?.telegram_chat_id && (
                      <Badge variant="outline" className="text-success border-success/30 bg-success/5 text-[10px] px-2 h-5">
                        ACTIVE
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground max-w-[460px] text-balance">
                    {user?.telegram_chat_id
                      ? <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" /> Receiving signals on chat <code className="bg-muted px-1 py-0.5 rounded text-xs font-mono text-foreground">{user.telegram_username ? `@${user.telegram_username}` : user.telegram_chat_id}</code></span>
                      : "Receive real-time trading signals, alerts, and strategy updates directly on your Telegram."}
                  </p>
                </div>

                <div className="flex-shrink-0">
                  {!user?.telegram_chat_id ? (
                    entitlements?.telegram_access ? (
                      <a
                        href={`https://t.me/TCopilot_bot?start=${user?.id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block w-full sm:w-auto"
                      >
                        <Button className="w-full sm:w-auto gap-2 shadow-sm" variant="default">
                          <Send className="w-4 h-4" />
                          Connect
                        </Button>
                      </a>
                    ) : (
                      <Link href="/pricing">
                        <Button className="w-full sm:w-auto gap-2 shadow-sm" variant="outline">
                          <Lock className="w-4 h-4" />
                          Upgrade to Connect
                        </Button>
                      </Link>
                    )
                  ) : (
                    <Button
                      variant="outline"
                      onClick={handleDisconnect}
                      className="w-full sm:w-auto hover:bg-destructive/10 hover:text-destructive hover:border-destructive/30 transition-colors"
                    >
                      Disconnect
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Subscription Section */}
        <Card className="bg-card border-border">
          <CardHeader>
            <div className="flex items-center gap-2">
              <CreditCard className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg">Subscription</CardTitle>
            </div>
            <CardDescription>Manage your plan and billing</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between rounded-lg bg-secondary/30 p-4">
              <div>
                <p className="font-medium text-foreground">Current Plan</p>
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant={['PRO', 'OWNER'].includes(entitlements?.tier || '') ? 'default' : 'secondary'}>
                    {planLabel}
                  </Badge>
                  {entitlements?.expires_at && (
                    <span className="text-sm text-muted-foreground">
                      Expires {new Date(entitlements.expires_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
              {!['PRO', 'OWNER'].includes(entitlements?.tier || '') && (
                <Link href="/pricing">
                  <Button>Upgrade</Button>
                </Link>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Preferences Section */}
        <Card className="bg-card border-border">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Globe className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg">Preferences</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="timezone">Timezone</Label>
                <p className="text-xs text-muted-foreground">Used for signal timestamps</p>
              </div>
              <Select value={timezone} onValueChange={handleUpdateTimezone}>
                <SelectTrigger id="timezone" className="w-48 bg-secondary/30">
                  <SelectValue placeholder="Select timezone" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="UTC">UTC (Universal Coordinated Time)</SelectItem>
                  <SelectItem value="America/New_York">New York (EST/EDT)</SelectItem>
                  <SelectItem value="America/Chicago">Chicago (CST/CDT)</SelectItem>
                  <SelectItem value="America/Denver">Denver (MST/MDT)</SelectItem>
                  <SelectItem value="America/Los_Angeles">Los Angeles (PST/PDT)</SelectItem>
                  <SelectItem value="America/Sao_Paulo">Sao Paulo (BRT)</SelectItem>
                  <SelectItem value="America/Argentina/Buenos_Aires">Buenos Aires (ART)</SelectItem>
                  <SelectItem value="Europe/London">London (GMT/BST)</SelectItem>
                  <SelectItem value="Europe/Madrid">Madrid (CET/CEST)</SelectItem>
                  <SelectItem value="Europe/Paris">Paris (CET/CEST)</SelectItem>
                  <SelectItem value="Europe/Moscow">Moscow (MSK)</SelectItem>
                  <SelectItem value="Asia/Dubai">Dubai (GST)</SelectItem>
                  <SelectItem value="Asia/Kolkata">Kolkata (IST)</SelectItem>
                  <SelectItem value="Asia/Bangkok">Bangkok (ICT)</SelectItem>
                  <SelectItem value="Asia/Singapore">Singapore (SGT)</SelectItem>
                  <SelectItem value="Asia/Tokyo">Tokyo (JST)</SelectItem>
                  <SelectItem value="Australia/Sydney">Sydney (AEST/AEDT)</SelectItem>
                  <SelectItem value="Pacific/Auckland">Auckland (NZST/NZDT)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Security Section */}
        <Card className="bg-card border-border">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              <CardTitle className="text-lg">Security</CardTitle>
            </div>
            <CardDescription>Protect your account</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Change Password</Label>
                <p className="text-xs text-muted-foreground">Confirm current password to set a new one</p>
              </div>
              <div className="flex flex-col gap-2 w-full max-w-sm">
                <Input
                  type="password"
                  placeholder="Current password"
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                />
                <div className="flex gap-2">
                  <Input
                    type="password"
                    placeholder="New password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                  />
                  <Button variant="outline" onClick={handleUpdatePassword} disabled={isLoading || !newPassword || !oldPassword}>Update</Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
