'use client'

import React, { useState, Suspense } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Eye, EyeOff, ArrowRight, Check, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ThemeToggle } from '@/components/theme-toggle'
import { cn } from '@/lib/utils'
import { useSearchParams } from 'next/navigation'
import SignupFormLoading from './loading'
import { useAuth } from '@/context/auth-context'
import { authService } from '@/services/auth'
import { BrandLogo } from '@/components/brand-logo'

const benefits = [
  'Access to BTC & ETH signals',
  '4H and 1D timeframes',
  'Full Swing Lite Access',
  'Strategy evaluation tools',
]

function SignupForm({ plan }: { plan: string | null }) {
  const router = useRouter()
  const { loginWithToken } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  const planConfig = {
    pro: { label: 'SwingPro', price: '$29/mo', color: 'text-primary' },
    trader: { label: 'SwingLite', price: '$10/mo', color: 'text-primary' },
    default: { label: 'Free Trial', price: '3 days free', color: 'text-success' },
  }

  const currentPlan = planConfig[plan as keyof typeof planConfig] || planConfig.default

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)
    try {
      // 1. Register
      await authService.register({ email, password, name })

      // 2. Auto Login
      const data = await authService.login(email, password)
      await loginWithToken(data.access_token)

      // 3. Redirect
      const next = new URLSearchParams(window.location.search).get('next') || '/dashboard'
      router.push(next)
    } catch (err: any) {
      if (err?.message?.includes('already exists')) {
        setError('User with this email already exists')
      } else {
        setError(err?.message || 'Signup failed')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full max-w-md animate-fade-up">
      {/* Card */}
      <div className="rounded-2xl border border-border/50 bg-card/80 backdrop-blur-xl p-8 shadow-lg">
        {/* Header */}
        <div className="text-center mb-8">
          {/* Plan badge */}
          <div className="inline-flex items-center gap-2 rounded-full border border-border/50 bg-secondary/50 px-4 py-1.5 mb-4">
            <span className={cn('text-sm font-medium', currentPlan.color)}>
              {currentPlan.label}
            </span>
            <span className="text-xs text-muted-foreground">{currentPlan.price}</span>
          </div>

          <h1 className="text-2xl font-semibold text-foreground mb-2">Create Your Account</h1>
          <p className="text-sm text-muted-foreground">Start your swing trading journey</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <Label htmlFor="name" className="text-sm font-medium">Full Name</Label>
            <Input
              id="name"
              type="text"
              placeholder="John Trader"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="h-11 bg-secondary/30 border-border/50 focus:border-primary focus:ring-primary/20"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email" className="text-sm font-medium">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="trader@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="h-11 bg-secondary/30 border-border/50 focus:border-primary focus:ring-primary/20"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-sm font-medium">Password</Label>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Create a strong password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-11 bg-secondary/30 border-border/50 pr-11 focus:border-primary focus:ring-primary/20"
                required
                minLength={8}
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute right-1 top-1/2 -translate-y-1/2 h-9 w-9 hover:bg-transparent"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <Eye className="h-4 w-4 text-muted-foreground" />
                )}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">Minimum 8 characters</p>
          </div>

          {/* Benefits for trial */}
          {!plan && (
            <div className="rounded-xl border border-border/50 bg-secondary/30 p-4 space-y-3">
              <p className="text-sm font-medium text-foreground">Your trial includes:</p>
              <ul className="space-y-2">
                {benefits.map((benefit) => (
                  <li key={benefit} className="flex items-center gap-2.5 text-sm text-muted-foreground">
                    <div className="flex h-4 w-4 items-center justify-center rounded-full bg-success/20">
                      <Check className="h-2.5 w-2.5 text-success" />
                    </div>
                    {benefit}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {error ? (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
              {error}
            </div>
          ) : null}

          <Button
            type="submit"
            className="w-full h-11 shadow-sm hover-lift"
            disabled={isLoading}
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                Creating account...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                {plan ? 'Continue to Payment' : 'Start Free Trial'}
                <ArrowRight className="h-4 w-4" />
              </span>
            )}
          </Button>
        </form>

        {/* Footer */}
        <div className="mt-8 pt-6 border-t border-border/50 text-center">
          <p className="text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link href="/auth/login" className="font-medium text-primary hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>

      {/* Disclaimer */}
      <p className="text-center text-xs text-muted-foreground/60 mt-6 px-4">
        By signing up, you agree to our{' '}
        <Link href="#" className="hover:text-muted-foreground">Terms of Service</Link>
        {' '}and{' '}
        <Link href="#" className="hover:text-muted-foreground">Privacy Policy</Link>.
      </p>
    </div>
  )
}

export default function SignupPage() {
  const searchParams = useSearchParams()
  const plan = searchParams.get('plan')

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Background */}
      <div className="fixed inset-0 -z-10">
        <div className="gradient-radial absolute inset-0" />
      </div>

      {/* Header */}
      <header className="border-b border-border/50 bg-background/80 backdrop-blur-xl">
        <div className="h-px bg-gradient-to-r from-transparent via-primary/20 to-transparent" />
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2.5">
            <BrandLogo showText={false} />
            <div className="flex flex-col">
              <span className="text-sm font-semibold tracking-tight text-foreground">TraderCopilot</span>
              <span className="text-[10px] font-medium text-muted-foreground -mt-0.5">Swing</span>
            </div>
          </Link>
          <ThemeToggle />
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-4">
        <Suspense fallback={<SignupFormLoading />}>
          <SignupForm plan={plan} />
        </Suspense>
      </main>
    </div>
  )
}
