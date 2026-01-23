'use client'

import React from 'react'
import { UserProvider, useUser } from '@/lib/user-context'
import { AppSidebar } from '@/components/app-sidebar'
import { AppHeader } from '@/components/app-header'
import { TrialExpiredScreen } from '@/components/trial-expired-screen'
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'

function DashboardContent({ children }: { children: React.ReactNode }) {
  const { isTrialExpired } = useUser()

  if (isTrialExpired) {
    return <TrialExpiredScreen />
  }

  return (
    <SidebarProvider>
      <div className="relative flex min-h-screen w-full bg-background">
        {/* Subtle background pattern */}
        <div className="fixed inset-0 -z-10 gradient-radial" />

        <AppSidebar />

        <SidebarInset className="flex flex-col">
          <AppHeader />

          <main className="flex-1 overflow-auto">
            <div className="container max-w-7xl p-6 lg:p-8">
              {children}
            </div>
          </main>

          {/* Footer */}
          <footer className="border-t border-border/40 py-4">
            <div className="container max-w-7xl px-6 lg:px-8">
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <p>TraderCopilot Swing</p>
                <p>Signals are for educational purposes only</p>
              </div>
            </div>
          </footer>
        </SidebarInset>
      </div>
    </SidebarProvider>
  )
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <UserProvider>
      <DashboardContent>{children}</DashboardContent>
    </UserProvider>
  )
}
