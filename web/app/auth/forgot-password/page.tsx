'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { ArrowRight, Mail } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ThemeToggle } from '@/components/theme-toggle'
import { authService } from '@/services/auth'
import { BrandLogo } from '@/components/brand-logo'

export default function ForgotPasswordPage() {
    const [email, setEmail] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [isSent, setIsSent] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError(null)
        setIsLoading(true)
        try {
            await authService.recoverPassword(email)
            setIsSent(true)
        } catch (err: any) {
            setError(err?.message || 'Failed to send recovery email')
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
                <div className="w-full max-w-md animate-fade-up">
                    {/* Card */}
                    <div className="rounded-2xl border border-border/50 bg-card/80 backdrop-blur-xl p-8 shadow-lg">
                        {/* Header */}
                        <div className="text-center mb-8">
                            <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                                <Mail className="h-6 w-6 text-primary" />
                            </div>
                            <h1 className="text-2xl font-semibold text-foreground mb-2">Reset Password</h1>
                            <p className="text-sm text-muted-foreground">
                                Enter your email address and we'll send you a link to reset your password.
                            </p>
                        </div>

                        {!isSent ? (
                            <form onSubmit={handleSubmit} className="space-y-5">
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
                                            Sending Link...
                                        </span>
                                    ) : (
                                        <span className="flex items-center gap-2">
                                            Send Reset Link
                                            <ArrowRight className="h-4 w-4" />
                                        </span>
                                    )}
                                </Button>
                            </form>
                        ) : (
                            <div className="text-center space-y-6">
                                <div className="rounded-lg border border-green-500/30 bg-green-500/10 px-4 py-4">
                                    <p className="text-sm text-green-200">
                                        Check your email! We've sent a password reset link to <strong>{email}</strong>.
                                    </p>
                                </div>
                                <div className="text-sm text-muted-foreground">
                                    Didn't receive the email? Check your spam folder or try again.
                                </div>
                                <Button variant="outline" onClick={() => setIsSent(false)} className="w-full">
                                    Try another email
                                </Button>
                            </div>
                        )}

                        {/* Footer */}
                        <div className="mt-8 pt-6 border-t border-border/50 text-center">
                            <Link href="/auth/login" className="text-sm font-medium text-primary hover:underline flex items-center justify-center gap-2">
                                Back to Sign In
                            </Link>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    )
}
