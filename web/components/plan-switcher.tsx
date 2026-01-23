'use client'

import { Settings2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useUser } from '@/lib/user-context'
import type { Plan } from '@/lib/types'

export function PlanSwitcher() {
  const { user, setPlan } = useUser()

  if (!user) return null

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2 text-xs bg-transparent">
          <Settings2 className="h-3.5 w-3.5" />
          Demo: Switch Plan
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuLabel>Demo Plan Switcher</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuRadioGroup value={user.plan} onValueChange={(value) => setPlan(value as Plan)}>
          <DropdownMenuRadioItem value="FREE">
            Trial (FREE)
          </DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="TRADER">
            SwingLite (TRADER)
          </DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="PRO">
            SwingPro (PRO)
          </DropdownMenuRadioItem>
        </DropdownMenuRadioGroup>
        <DropdownMenuSeparator />
        <p className="px-2 py-1.5 text-xs text-muted-foreground">
          Switch plans to test gating
        </p>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
