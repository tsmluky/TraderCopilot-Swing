'use client'

import { useState, useEffect } from 'react'
import { User, Shield, CreditCard, Bell, Moon, Globe, Send, Lock, ChevronRight, Key } from 'lucide-react'
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
import { billingService } from '@/services/billing'
import { toast } from 'sonner'
import Link from 'next/link'
import { cn } from '@/lib/utils'

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

  const handleManageSubscription = async () => {
    try {
      setIsLoading(true)
      const res = await billingService.createPortalSession()
      if (res?.url) {
        window.location.href = res.url
      } else {
        toast.error("Could not generate portal link")
      }
    } catch (e: any) {
      // Handle specific case where user is PRO but has no Stripe ID (e.g. gifted)
      if (e.message?.includes("NO_BILLING_CUSTOMER")) {
        toast.error("Subscription managed manually. Contact support.")
      } else {
        toast.error("Failed to access billing portal")
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="relative space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">

      {/* Background Ambient Glow - Adjusted for Light Mode */}
      <div className="absolute top-0 right-0 -z-10 h-[500px] w-[500px] bg-primary/5 blur-[120px] rounded-full pointer-events-none opacity-40 mix-blend-multiply dark:mix-blend-normal" />
      <div className="absolute bottom-0 left-0 -z-10 h-[300px] w-[300px] bg-blue-500/5 blur-[100px] rounded-full pointer-events-none opacity-20 mix-blend-multiply dark:mix-blend-normal" />

      {/* Header */}
      <div className="flex flex-col gap-2 border-b border-black/5 dark:border-white/5 pb-4">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          Settings
        </h1>
        <p className="text-lg text-muted-foreground/80 font-light max-w-2xl">
          Manage your trading profile, security preferences, and subscription plan.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-12">

        {/* Left Column (Main Profile) - Span 8 */}
        <div className="lg:col-span-8 space-y-8">

          {/* Subscription Card - Fixed Contrast */}
          <Card className="relative overflow-hidden border-black/5 dark:border-primary/20 bg-gradient-to-br from-white via-white/80 to-primary/5 dark:from-card/80 dark:via-card/50 dark:to-primary/5 backdrop-blur-md transition-all duration-300 hover:shadow-2xl hover:shadow-primary/5 hover:border-primary/30 group rounded-3xl">
            <div className="absolute inset-0 bg-grid-black/5 dark:bg-grid-white/5 mask-image-linear-gradient-to-b opacity-50 group-hover:opacity-100 transition-opacity" />
            <div className="absolute top-0 right-0 p-4 opacity-50 group-hover:opacity-100 transition-opacity">
              <div className="h-40 w-40 bg-primary/10 blur-[80px] rounded-full" />
            </div>

            <CardHeader className="pb-4 relative z-10">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-5">
                  <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 flex items-center justify-center border border-primary/20 shadow-inner group-hover:scale-105 transition-transform duration-300">
                    <CreditCard className="h-7 w-7 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-2xl font-bold">Subscription Plan</CardTitle>
                    <CardDescription className="text-base mt-0.5">Manage your billing and tier capabilities</CardDescription>
                  </div>
                </div>
                <Badge variant={['PRO', 'SWINGPRO', 'OWNER'].includes(user?.plan?.toUpperCase() || '') ? 'default' : 'secondary'} className="px-5 py-1.5 h-auto text-sm shadow-glow-sm uppercase tracking-wider font-bold rounded-lg">
                  {user?.plan || 'Free'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="relative z-10 pb-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between bg-white/50 dark:bg-black/20 backdrop-blur-xl rounded-2xl p-4 border border-black/5 dark:border-white/10 shadow-sm dark:shadow-inner gap-4">
                <div className="space-y-1">
                  <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Current Status</div>
                  <div className="flex flex-col sm:flex-row sm:items-baseline gap-2">
                    <span className="text-3xl font-black text-foreground tracking-tight">Active</span>
                    {user?.plan_expires_at && (
                      <span className="text-sm text-foreground/60 font-medium">
                        Renews on {new Date(user.plan_expires_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}
                      </span>
                    )}
                  </div>
                </div>
                {!['PRO', 'SWINGPRO', 'OWNER', 'PREMIUM'].includes(user?.plan?.toUpperCase() || '') ? (
                  <Link href="/pricing">
                    <Button className="shadow-xl shadow-primary/20 bg-gradient-to-r from-primary to-primary/70 hover:scale-105 transition-all duration-300 h-12 px-8 text-base rounded-xl font-bold">
                      Upgrade to PRO <ChevronRight className="ml-2 w-4 h-4" />
                    </Button>
                  </Link>
                ) : (
                  // Billing Portal / Manage for PRO users
                  <Button
                    variant="outline"
                    className="border-black/5 dark:border-white/10 hover:bg-black/5 dark:hover:bg-white/5 h-12 px-8 rounded-xl font-bold hover:border-black/10 dark:hover:border-white/20"
                    onClick={handleManageSubscription}
                    disabled={isLoading}
                  >
                    Manage Subscription
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Profile Info - Light Mode Fixes */}
          <Card className="bg-white/60 dark:bg-card/30 backdrop-blur-xl border-black/5 dark:border-white/5 hover:bg-white/80 dark:hover:bg-card/40 transition-colors rounded-3xl overflow-hidden shadow-sm dark:shadow-none">
            <div className="h-1 w-full bg-gradient-to-r from-transparent via-black/5 dark:via-white/10 to-transparent opacity-50" />
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-xl bg-black/5 dark:bg-white/5 flex items-center justify-center border border-black/5 dark:border-white/5">
                  <User className="h-5 w-5 text-muted-foreground" />
                </div>
                <div>
                  <CardTitle className="text-lg font-bold">Personal Details</CardTitle>
                  <CardDescription>Your public identity information</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2.5">
                  <Label htmlFor="name" className="text-[10px] uppercase text-muted-foreground/70 font-bold tracking-widest pl-1">Full Name</Label>
                  <div className="relative group">
                    <Input id="name" value={user?.name || ''} readOnly className="rounded-xl bg-black/5 dark:bg-black/20 border-black/5 dark:border-white/5 hover:border-black/10 dark:hover:border-white/10 transition-all pl-10 h-12 font-medium text-foreground/90 focus-visible:ring-primary/20" />
                    <User className="absolute left-3.5 top-4 h-4 w-4 text-muted-foreground/50 group-hover:text-primary/50 transition-colors" />
                  </div>
                </div>
                <div className="space-y-2.5">
                  <Label htmlFor="email" className="text-[10px] uppercase text-muted-foreground/70 font-bold tracking-widest pl-1">Email Address</Label>
                  <div className="relative group">
                    <Input id="email" value={user?.email || ''} className="rounded-xl bg-black/5 dark:bg-black/20 border-black/5 dark:border-white/5 hover:border-black/10 dark:hover:border-white/10 transition-all pl-10 h-12 font-medium text-foreground/90 focus-visible:ring-primary/20" readOnly />
                    <div className="absolute left-3.5 top-4 h-4 w-4 text-muted-foreground/50 group-hover:text-primary/50 transition-colors font-mono font-bold flex items-center justify-center">@</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Security - Light Mode Fixes */}
          <Card className="bg-white/60 dark:bg-card/30 backdrop-blur-xl border-black/5 dark:border-white/5 hover:bg-white/80 dark:hover:bg-card/40 transition-colors rounded-3xl overflow-hidden shadow-sm dark:shadow-none">
            <div className="h-1 w-full bg-gradient-to-r from-transparent via-black/5 dark:via-white/10 to-transparent opacity-50" />
            <CardHeader>
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-xl bg-black/5 dark:bg-white/5 flex items-center justify-center border border-black/5 dark:border-white/5">
                  <Shield className="h-5 w-5 text-muted-foreground" />
                </div>
                <div>
                  <CardTitle className="text-lg font-bold">Security</CardTitle>
                  <CardDescription>Password and authentication</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2.5">
                    <Label className="text-[10px] uppercase text-muted-foreground/70 font-bold tracking-widest pl-1">Current Password</Label>
                    <div className="relative group">
                      <Input
                        type="password"
                        placeholder="••••••••••••"
                        value={oldPassword}
                        onChange={(e) => setOldPassword(e.target.value)}
                        className="rounded-xl bg-black/5 dark:bg-black/20 border-black/5 dark:border-white/5 hover:border-black/10 dark:hover:border-white/10 h-12 pl-10 focus-visible:ring-primary/20"
                      />
                      <Key className="absolute left-3.5 top-4 h-4 w-4 text-muted-foreground/50 group-hover:text-primary/50 transition-colors" />
                    </div>
                  </div>
                  <div className="space-y-2.5">
                    <Label className="text-[10px] uppercase text-muted-foreground/70 font-bold tracking-widest pl-1">New Password</Label>
                    <div className="relative group">
                      <Input
                        type="password"
                        placeholder="••••••••••••"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="rounded-xl bg-black/5 dark:bg-black/20 border-black/5 dark:border-white/5 hover:border-black/10 dark:hover:border-white/10 h-12 pl-10 focus-visible:ring-primary/20"
                      />
                      <Lock className="absolute left-3.5 top-4 h-4 w-4 text-muted-foreground/50 group-hover:text-primary/50 transition-colors" />
                    </div>
                  </div>
                </div>
                <div className="flex justify-end pt-2">
                  <Button
                    variant="secondary"
                    onClick={handleUpdatePassword}
                    disabled={isLoading || !newPassword || !oldPassword}
                    className="min-w-[140px] h-11 font-bold rounded-xl bg-black/5 hover:bg-black/10 dark:bg-white/10 dark:hover:bg-white/15 text-foreground"
                  >
                    Update Password
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

        </div>

        {/* Right Column (Integrations & Prefs) - Span 4 */}
        <div className="lg:col-span-4 space-y-8">

          {/* Telegram Integration - Enhanced Light Mode */}
          <Card className="border-black/5 dark:border-border/60 bg-gradient-to-b from-white to-[#2AABEE]/5 dark:from-card/60 dark:to-[#2AABEE]/5 overflow-hidden hover:border-[#2AABEE]/30 transition-colors rounded-3xl shadow-sm dark:shadow-none">
            {/* Header with improved background containment */}
            <div className="bg-[#2AABEE]/5 border-b border-[#2AABEE]/10 px-4 py-3">
              <div className="flex items-center gap-4">
                <div className="h-10 w-10 rounded-xl bg-[#2AABEE]/10 dark:bg-[#2AABEE]/20 flex items-center justify-center border border-[#2AABEE]/20 dark:border-[#2AABEE]/30 shadow-lg shadow-[#2AABEE]/10">
                  <Send className="h-5 w-5 text-[#2AABEE]" />
                </div>
                <div>
                  <CardTitle className="text-base font-bold text-foreground">Telegram Bot</CardTitle>
                  <CardDescription className="text-xs font-medium opacity-80">Notifications & Alerts</CardDescription>
                </div>
              </div>
            </div>
            <CardContent className="space-y-4 pt-4">
              {user?.telegram_chat_id ? (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl bg-background/50 border border-black/5 dark:border-border/50 flex flex-col items-center text-center gap-2 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-gradient-to-br from-[#2AABEE]/10 to-transparent opacity-50 transition-opacity group-hover:opacity-80" />
                    <div className="h-2.5 w-2.5 rounded-full bg-success shadow-[0_0_10px_rgba(34,197,94,0.6)] animate-pulse" />
                    <span className="text-sm font-bold text-foreground z-10">Connected & Active</span>
                    <code className="text-[10px] text-muted-foreground font-mono bg-black/5 dark:bg-black/40 px-3 py-1 rounded-full z-10 border border-black/5 dark:border-white/5">
                      {user.telegram_username ? `@${user.telegram_username}` : user.telegram_chat_id}
                    </code>
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleDisconnect}
                    className="w-full text-xs font-semibold text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors rounded-xl h-9"
                  >
                    Disconnect Account
                  </Button>
                </div>
              ) : (
                <div className="space-y-5">
                  <div className="p-4 rounded-2xl bg-[#2AABEE]/5 border border-[#2AABEE]/10 text-xs text-muted-foreground leading-relaxed">
                    <span className="font-bold text-[#2AABEE] block mb-1.5 uppercase tracking-wide text-[10px]">Why connect?</span>
                    Receive instant alerts for trade setups, execution updates, and strategy signals directly on your phone.
                  </div>

                  {(entitlements?.telegram_access || ['PRO', 'SWINGPRO', 'OWNER'].includes(user?.plan?.toUpperCase() || '')) ? (
                    <a
                      href={`https://t.me/TCopilot_bot?start=${user?.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block"
                    >
                      <Button className="w-full bg-[#2AABEE] hover:bg-[#2AABEE]/90 text-white shadow-lg shadow-[#2AABEE]/20 h-11 font-bold tracking-wide rounded-xl transition-transform hover:scale-[1.02]">
                        <Send className="w-4 h-4 mr-2" /> CONNECT BOT
                      </Button>
                    </a>
                  ) : (
                    <Link href="/pricing" className="block">
                      <Button variant="outline" className="w-full border-dashed border-2 h-11 hover:border-primary/50 hover:text-primary transition-all rounded-xl font-medium">
                        <Lock className="w-4 h-4 mr-2 opacity-50" />
                        Unlock Integration
                      </Button>
                    </Link>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Timezone */}
          <Card className="bg-white/60 dark:bg-card/30 backdrop-blur-xl border-black/5 dark:border-white/5 hover:bg-white/80 dark:hover:bg-card/40 transition-colors rounded-3xl overflow-hidden shadow-sm dark:shadow-none">
            <div className="h-1 w-full bg-gradient-to-r from-transparent via-black/5 dark:via-white/10 to-transparent opacity-50" />
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-xl bg-black/5 dark:bg-white/5 flex items-center justify-center border border-black/5 dark:border-white/5">
                  <Globe className="h-5 w-5 text-muted-foreground" />
                </div>
                <div>
                  <CardTitle className="text-base font-bold">Localization</CardTitle>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <Label className="text-[10px] uppercase text-muted-foreground/70 font-bold tracking-widest pl-1">Trading Timezone</Label>
                <Select value={timezone} onValueChange={handleUpdateTimezone}>
                  <SelectTrigger className="w-full bg-black/5 dark:bg-black/20 h-10 border-black/5 dark:border-white/5 rounded-xl font-medium focus:ring-primary/20">
                    <SelectValue placeholder="Select timezone" />
                  </SelectTrigger>
                  <SelectContent className="rounded-xl border-black/5 dark:border-white/5 bg-white/90 dark:bg-black/90 backdrop-blur-xl">
                    <SelectItem value="UTC">UTC (Universal)</SelectItem>
                    <SelectItem value="America/New_York">New York (Eastern)</SelectItem>
                    <SelectItem value="America/Chicago">Chicago (Central)</SelectItem>
                    <SelectItem value="America/Los_Angeles">Los Angeles (Pacific)</SelectItem>
                    <SelectItem value="Europe/London">London (GMT)</SelectItem>
                    <SelectItem value="Europe/Madrid">Madrid (CET)</SelectItem>
                    <SelectItem value="Europe/Paris">Paris (CET)</SelectItem>
                    <SelectItem value="America/Argentina/Buenos_Aires">Buenos Aires (ART)</SelectItem>
                    <SelectItem value="Asia/Tokyo">Tokyo (JST)</SelectItem>
                    <SelectItem value="Australia/Sydney">Sydney (AEST)</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-[10px] text-muted-foreground leading-tight px-1">
                  All signals and strategy timestamps will be converted to this timezone.
                </p>
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  )
}
