'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
    LayoutDashboard,
    TrendingUp,
    BarChart3,
    MessageSquare,
    Settings,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUser } from '@/lib/user-context'

const navigation = [
    { name: 'Home', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Signals', href: '/dashboard/signals', icon: TrendingUp },
    { name: 'Advisor', href: '/dashboard/advisor', icon: MessageSquare },
    { name: 'Stats', href: '/dashboard/strategies', icon: BarChart3 },
    { name: 'Settings', href: '/dashboard/settings', icon: Settings },
]

export function MobileNav() {
    const pathname = usePathname()
    const { canAccessAdvisor } = useUser()

    return (
        <nav className="fixed bottom-0 left-0 right-0 z-50 md:hidden pb-safe">
            <div className="mx-4 mb-4 rounded-2xl bg-zinc-900/90 backdrop-blur-xl border border-white/10 shadow-2xl overflow-hidden">
                <div className="flex items-center justify-around h-16">
                    {navigation.map((item) => {
                        const isActive = item.href === '/dashboard'
                            ? pathname === '/dashboard'
                            : pathname.startsWith(item.href)

                        // Handle Advisor Lock logic visually
                        const isAdvisor = item.name === 'Advisor'
                        const isLocked = isAdvisor && !canAccessAdvisor

                        return (
                            <Link
                                key={item.name}
                                href={isLocked ? '#' : item.href}
                                className={cn(
                                    "relative flex flex-col items-center justify-center w-full h-full transition-all duration-300",
                                    isActive ? "text-emerald-400" : "text-zinc-500 hover:text-zinc-300",
                                    isLocked && "opacity-50 grayscale"
                                )}
                            >
                                {/* Active Indicator Line */}
                                {isActive && (
                                    <div className="absolute top-0 w-8 h-0.5 rounded-b-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
                                )}

                                <div className={cn(
                                    "p-1.5 rounded-xl transition-all",
                                    isActive && "bg-emerald-500/10 translate-y-[-2px]"
                                )}>
                                    <item.icon className={cn("w-5 h-5", isActive && "fill-current")} />
                                </div>

                                <span className="text-[10px] font-medium mt-0.5">{item.name}</span>
                            </Link>
                        )
                    })}
                </div>
            </div>
        </nav>
    )
}
