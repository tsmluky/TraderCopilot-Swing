'use client'

import React, { useState, Suspense } from 'react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { ArrowRight, Key, Eye, EyeOff } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ThemeToggle } from '@/components/theme-toggle'
import { authService } from '@/services/auth'
import { BrandLogo } from '@/components/brand-logo'

function ResetPasswordContent() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const token = searchParams.get('token')

    const [isLoading, setIsLoading] = useState(false)
    const [isSuccess, setIsSuccess] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [showPassword, setShowPassword] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError(null)

        if (!token) {
            setError('Invalid or missing recovery token.')
            return
        }

        if (password !== confirmPassword) {
            setError('Passwords do not match.')
            return
        }

        if (password.length < 6) {
            setError('Password must be at least 6 characters.')
            return
        }

        setIsLoading(true)
        try {
            await authService.resetPassword(token, password)
            setIsSuccess(true)
        } catch (err: any) {
            setError(err?.message || 'Failed to reset password. Token may be expired.')
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-background flex flex-col">
            {/* Background */}
            <div className="fixed inset-0 -z-10">
                <div className="gradient-radial absolute inset-0" />
            </div>

            {/* Header */}
            <header className="border-b border-border/50 bg-background/80 backdrop-blur-xl">
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
                <div className="w-full max-w-md animate-fade-up">
                    <div className="rounded-2xl border border-border/50 bg-card/80 backdrop-blur-xl p-8 shadow-lg">

                        {/* Header */}
                        <div className="text-center mb-8">
                            <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                                <Key className="h-6 w-6 text-primary" />
                            </div>
                            <h1 className="text-2xl font-semibold text-foreground mb-2">Set New Password</h1>
                            <p className="text-sm text-muted-foreground">
                                Ensure your account is secure with a strong password.
                            </p>
                        </div>

                        {!isSuccess ? (
                            <form onSubmit={handleSubmit} className="space-y-5">

                                <div className="space-y-2">
                                    <Label htmlFor="password">New Password</Label>
                                    <div className="relative">
                                        <Input
                                            id="password"
                                            type={showPassword ? 'text' : 'password'}
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            placeholder="••••••••"
                                            className="h-11 bg-secondary/30 pr-11"
                                            required
                                        />
                                        <Button
                                            type="button"
                                            variant="ghost"
                                            size="icon"
                                            className="absolute right-1 top-1/2 -translate-y-1/2 h-9 w-9 hover:bg-transparent"
                                            onClick={() => setShowPassword(!showPassword)}
                                        >
                                            {showPassword ? <EyeOff className="h-4 w-4 text-muted-foreground" /> : <Eye className="h-4 w-4 text-muted-foreground" />}
                                        </Button>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="confirmPassword">Confirm Password</Label>
                                    <Input
                                        id="confirmPassword"
                                        type="password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        placeholder="••••••••"
                                        className="h-11 bg-secondary/30"
                                        required
                                    />
                                </div>

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
                                        'Resetting...'
                                    ) : (
                                        <span className="flex items-center gap-2">
                                            Reset Password
                                            <ArrowRight className="h-4 w-4" />
                                        </span>
                                    )}
                                </Button>
                            </form>
                        ) : (
                            <div className="text-center space-y-6">
                                <div className="rounded-lg border border-green-500/30 bg-green-500/10 px-4 py-4">
                                    <p className="text-sm text-green-200">
                                        <strong>Success!</strong> Your password has been updated.
                                    </p>
                                </div>
                                <Link href="/auth/login">
                                    <Button className="w-full h-11">
                                        Sign In with New Password
                                    </Button>
                                </Link>
                            </div>
                        )}

                        {!isSuccess && (
                            <div className="mt-8 pt-6 border-t border-border/50 text-center">
                                <Link href="/auth/login" className="text-sm font-medium text-primary hover:underline">
                                    Back to Sign In
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    )
}

export default function ResetPasswordPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-background flex items-center justify-center">Loading...</div>}>
            <ResetPasswordContent />
        </Suspense>
    )
}
