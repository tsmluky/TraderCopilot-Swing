'use client'

import { Bell, Settings, CreditCard, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/theme-toggle'
import { SidebarTrigger } from '@/components/ui/sidebar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { useUser } from '@/lib/user-context'
import Link from 'next/link'

import { usePathname } from 'next/navigation'

export function AppHeader() {
  const { user, logout } = useUser()
  const pathname = usePathname()

  // Get current page name from path
  const segments = pathname?.split('/').filter(Boolean) || []
  const currentPage = segments[segments.length - 1]

  // Format page name: "strategies" -> "Strategies"
  const pageTitle = (currentPage && currentPage !== 'dashboard')
    ? currentPage.charAt(0).toUpperCase() + currentPage.slice(1)
    : 'Overview'

  const initials =
    user?.name
      ?.split(' ')
      .filter(Boolean)
      .map((n) => n[0])
      .join('')
      .toUpperCase() || 'TC'

  const firstName = user?.name?.split(' ')?.[0] || '—'

  const planLabel =
    !user?.plan
      ? '—'
      : user.plan === 'FREE'
        ? 'Trial'
        : user.plan === 'TRADER'
          ? 'SwingLite'
          : 'SwingPro'

  return (
    <header className="sticky top-0 z-40 w-full">
      {/* Premium top accent line */}
      <div className="h-px bg-gradient-to-r from-transparent via-primary/20 to-transparent" />

      <div className="flex h-14 items-center justify-between border-b border-border/50 bg-background/80 px-4 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
        {/* Left side */}
        <div className="flex items-center gap-3">
          <SidebarTrigger className="h-8 w-8 text-muted-foreground hover:text-foreground transition-colors md:hidden" />

          {/* Breadcrumb */}
          <nav className="hidden md:flex items-center gap-1.5 text-sm">
            <Link href="/dashboard" className="text-muted-foreground/70 hover:text-foreground transition-colors">
              Dashboard
            </Link>
            <span className="text-muted-foreground/40">/</span>
            <span className="font-medium text-foreground">{pageTitle}</span>
          </nav>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-2">
          {/* Theme Toggle */}
          <ThemeToggle />

          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="relative h-9 w-9 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition-premium"
                suppressHydrationWarning
              >
                <Bell className="h-4 w-4" />
                {/* 
                <span className="absolute -right-0.5 -top-0.5 flex h-4 w-4">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary/50 opacity-75" />
                  <span className="relative inline-flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] font-semibold text-primary-foreground">
                    1
                  </span>
                </span>
                */}
                <span className="sr-only">Notifications</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80 border-border/50 bg-popover/95 backdrop-blur-xl shadow-premium-lg">
              <DropdownMenuLabel className="font-semibold">Notifications</DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-border/50" />
              <div className="p-4 text-center text-sm text-muted-foreground">
                <p>You're all caught up!</p>
                <p className="text-xs mt-1 opacity-70">No new alerts or messages.</p>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className="h-9 gap-2.5 rounded-lg px-2 hover:bg-accent transition-premium"
                suppressHydrationWarning
              >
                <Avatar className="h-7 w-7 border border-border/50">
                  <AvatarFallback className="bg-primary/10 text-primary text-xs font-semibold">
                    {initials}
                  </AvatarFallback>
                </Avatar>
                <div className="hidden lg:flex flex-col items-start">
                  <span className="text-xs font-medium leading-none">{firstName}</span>
                  <span className="text-[10px] text-muted-foreground leading-none mt-0.5">
                    {planLabel}
                  </span>
                </div>
              </Button>
            </DropdownMenuTrigger>

            <DropdownMenuContent
              align="end"
              className="w-56 border-border/50 bg-popover/95 backdrop-blur-xl shadow-premium-lg"
            >
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">{user?.name ?? 'Loading…'}</p>
                  <p className="text-xs leading-none text-muted-foreground">{user?.email ?? ''}</p>
                </div>
              </DropdownMenuLabel>

              <DropdownMenuSeparator className="bg-border/50" />

              <DropdownMenuItem asChild className="cursor-pointer gap-2">
                <Link href="/dashboard/settings">
                  <Settings className="h-4 w-4 text-muted-foreground" />
                  Account Settings
                </Link>
              </DropdownMenuItem>

              <DropdownMenuItem asChild className="cursor-pointer gap-2">
                <Link href="/pricing">
                  <CreditCard className="h-4 w-4 text-muted-foreground" />
                  Manage Subscription
                </Link>
              </DropdownMenuItem>

              <DropdownMenuSeparator className="bg-border/50" />

              <DropdownMenuItem
                className="cursor-pointer gap-2 text-muted-foreground hover:text-foreground"
                onSelect={(e) => {
                  e.preventDefault()
                  logout()
                }}
              >
                <LogOut className="h-4 w-4" />
                Sign Out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}
