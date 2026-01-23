'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  TrendingUp,
  BarChart3,
  MessageSquare,
  Settings,
  Lock,
  Sparkles,
  ArrowUpRight,
  Shield,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { BrandLogo } from '@/components/brand-logo'
import { useUser } from '@/lib/user-context'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  useSidebar,
} from '@/components/ui/sidebar'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

const navigation = [
  { name: 'Overview', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Signals', href: '/dashboard/signals', icon: TrendingUp },
  { name: 'Strategies', href: '/dashboard/strategies', icon: BarChart3 },
  { name: 'Advisor', href: '/dashboard/advisor', icon: MessageSquare, proOnly: true },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
  { name: 'Admin', href: '/dashboard/admin', icon: Shield, adminOnly: true },
]

export function AppSidebar() {
  const pathname = usePathname()
  const { user, canAccessAdvisor } = useUser()
  const { state } = useSidebar()
  const isCollapsed = state === 'collapsed'

  const planLabel = user?.plan === 'FREE' ? 'Trial' : user?.plan === 'TRADER' ? 'SwingLite' : 'SwingPro'

  return (
    <TooltipProvider delayDuration={0}>
      <Sidebar collapsible="icon" className="border-r-0">
        {/* Header */}
        <SidebarHeader className="border-b border-sidebar-border/50">
          <div className="flex h-14 items-center px-4">
            <Link href="/dashboard" className="flex items-center gap-2">
              {/* Logo mark */}
              <BrandLogo showText={false} />

              {/* Logo text - hidden when collapsed */}
              <div className={cn('flex flex-col transition-opacity', isCollapsed && 'opacity-0 w-0 overflow-hidden')}>
                <span className="text-sm font-semibold tracking-tight text-foreground">TraderCopilot</span>
                <span className="text-[10px] font-medium text-muted-foreground -mt-0.5">Swing</span>
              </div>
            </Link>
          </div>
        </SidebarHeader>

        {/* Navigation */}
        <SidebarContent className="px-2 py-4">
          <SidebarGroup>
            <SidebarGroupContent>
              <SidebarMenu className="gap-1">
                {navigation.map((item) => {
                  const isActive = item.href === '/dashboard'
                    ? pathname === '/dashboard'
                    : pathname.startsWith(item.href)

                  // Filter out Admin items if not owner
                  // Allow if plan is OWNER OR if email matches the hardcoded owner email
                  if ((item as any).adminOnly) {
                    const isOwner = user?.plan === 'OWNER' || user?.email === 'tsmluky@gmail.com'
                    if (!isOwner) return null
                  }

                  const isLocked = item.proOnly && !canAccessAdvisor

                  return (
                    <SidebarMenuItem key={item.name}>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <SidebarMenuButton
                            asChild
                            isActive={isActive}
                            className={cn(
                              'h-10 gap-3 rounded-lg px-3 transition-all duration-200',
                              isActive
                                ? 'bg-sidebar-accent text-sidebar-accent-foreground shadow-soft-xs'
                                : 'text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground',
                              isLocked && 'opacity-50'
                            )}
                          >
                            <Link
                              href={isLocked ? '#' : item.href}
                              onClick={(e) => isLocked && e.preventDefault()}
                              className="flex items-center gap-3"
                            >
                              <item.icon className={cn(
                                'h-4 w-4 shrink-0 transition-colors',
                                isActive ? 'text-primary' : 'text-sidebar-foreground/50'
                              )} />
                              <span className="flex-1 text-sm font-medium">{item.name}</span>

                              {/* Lock or PRO badge */}
                              {item.proOnly && (
                                isLocked ? (
                                  <Lock className="h-3 w-3 text-sidebar-foreground/40" />
                                ) : (
                                  <span className="flex h-4 items-center rounded bg-primary/15 px-1.5 text-[10px] font-semibold text-primary">
                                    PRO
                                  </span>
                                )
                              )}
                            </Link>
                          </SidebarMenuButton>
                        </TooltipTrigger>
                        {isCollapsed && (
                          <TooltipContent side="right" className="flex items-center gap-2">
                            {item.name}
                            {isLocked && <Lock className="h-3 w-3" />}
                          </TooltipContent>
                        )}
                      </Tooltip>
                    </SidebarMenuItem>
                  )
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>

        {/* Footer */}
        <SidebarFooter className="border-t border-sidebar-border/50 p-3">
          {/* Plan indicator */}
          <Link href="/pricing" className="block outline-none">
            <div className={cn(
              'rounded-lg p-3 transition-all hover:bg-sidebar-accent cursor-pointer group',
              user?.plan === 'PRO' && 'bg-primary/5 hover:bg-primary/10'
            )}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={cn(
                    'flex h-8 w-8 items-center justify-center rounded-lg transition-colors',
                    user?.plan === 'PRO' ? 'bg-primary/10 text-primary group-hover:bg-primary/20' : 'bg-sidebar-foreground/5 text-sidebar-foreground/60 group-hover:bg-sidebar-foreground/10'
                  )}>
                    <Sparkles className="h-4 w-4" />
                  </div>
                  <div className={cn('flex flex-col text-left', isCollapsed && 'hidden')}>
                    <span className="text-xs font-semibold text-sidebar-foreground group-hover:text-primary transition-colors">
                      {planLabel}
                    </span>
                    {user?.plan === 'FREE' ? (
                      <span className="text-[10px] text-muted-foreground">
                        {user.trialExpiresAt
                          ? Math.max(0, Math.ceil((new Date(user.trialExpiresAt).getTime() - Date.now()) / (1000 * 60 * 60 * 24)))
                          : 0} days left
                      </span>
                    ) : (
                      <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                        Active Subscription <ArrowUpRight className="h-2 w-2 opacity-50" />
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </Link>
        </SidebarFooter>

        <SidebarRail />
      </Sidebar>
    </TooltipProvider>
  )
}
