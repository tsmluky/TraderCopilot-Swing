'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { BrandLogo } from '@/components/brand-logo'
import { cn } from '@/lib/utils'

export function SiteHeader() {
    const [isScrolled, setIsScrolled] = useState(false)

    useEffect(() => {
        const handleScroll = () => setIsScrolled(window.scrollY > 20)
        window.addEventListener('scroll', handleScroll)
        return () => window.removeEventListener('scroll', handleScroll)
    }, [])

    return (
        <header
            className={cn(
                'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
                isScrolled ? 'bg-black/80 backdrop-blur-xl border-b border-white/10' : 'bg-transparent'
            )}
        >
            <div className="container max-w-7xl mx-auto flex h-16 items-center justify-between px-4 lg:px-8 relative">
                <Link href="/" className="block">
                    <BrandLogo textSize="text-sm text-white" />
                </Link>

                <nav className="hidden md:flex items-center gap-6 absolute left-1/2 -translate-x-1/2">
                    <Link href="/#features" className="text-sm font-medium text-muted-foreground hover:text-white transition-colors">
                        Features
                    </Link>
                    <Link href="/#pricing" className="text-sm font-medium text-muted-foreground hover:text-white transition-colors">
                        Pricing
                    </Link>
                    <Link href="/#transparency" className="text-sm font-medium text-muted-foreground hover:text-white transition-colors">
                        Resources
                    </Link>
                </nav>

                <div className="flex items-center gap-3 ml-auto md:ml-0">
                    <Link href="/auth/login" className="hidden sm:block">
                        <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-white">
                            Log in
                        </Button>
                    </Link>
                    <Link href="/auth/signup">
                        <Button size="sm" className="bg-white text-black hover:bg-white/90 font-medium rounded-full px-5">
                            Get Started
                        </Button>
                    </Link>
                </div>
            </div>
        </header>
    )
}
