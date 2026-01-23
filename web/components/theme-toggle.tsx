'use client'

import * as React from 'react'
import { Moon, Sun, Monitor, Laptop } from 'lucide-react'
import { useTheme } from 'next-themes'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'

export function ThemeToggle({ className }: { className?: string }) {
  const { theme, setTheme, resolvedTheme } = useTheme()
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <Button
        variant="ghost"
        size="icon"
        className={cn(
          'h-9 w-9 rounded-lg border border-border/50 bg-card/50',
          className
        )}
      >
        <span className="h-4 w-4" />
      </Button>
    )
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className={cn(
            'h-9 w-9 rounded-lg border border-border/50 bg-card/80 backdrop-blur-sm',
            'hover:bg-accent hover:border-border transition-all duration-200',
            'focus-visible:ring-1 focus-visible:ring-ring',
            className
          )}
        >
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all duration-300 dark:-rotate-90 dark:scale-0 text-foreground" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all duration-300 dark:rotate-0 dark:scale-100 text-foreground" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent 
        align="end" 
        className="min-w-[160px] border-border/60 bg-card/95 backdrop-blur-xl shadow-soft-lg"
      >
        <DropdownMenuItem 
          onClick={() => setTheme('light')}
          className={cn(
            'flex items-center gap-3 cursor-pointer py-2.5',
            theme === 'light' && 'bg-accent'
          )}
        >
          <Sun className="h-4 w-4 text-muted-foreground" />
          <span className="font-medium">Light</span>
          {theme === 'light' && (
            <span className="ml-auto h-2 w-2 rounded-full bg-primary" />
          )}
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => setTheme('dark')}
          className={cn(
            'flex items-center gap-3 cursor-pointer py-2.5',
            theme === 'dark' && 'bg-accent'
          )}
        >
          <Moon className="h-4 w-4 text-muted-foreground" />
          <span className="font-medium">Dark</span>
          {theme === 'dark' && (
            <span className="ml-auto h-2 w-2 rounded-full bg-primary" />
          )}
        </DropdownMenuItem>
        <DropdownMenuItem 
          onClick={() => setTheme('system')}
          className={cn(
            'flex items-center gap-3 cursor-pointer py-2.5',
            theme === 'system' && 'bg-accent'
          )}
        >
          <Laptop className="h-4 w-4 text-muted-foreground" />
          <span className="font-medium">System</span>
          {theme === 'system' && (
            <span className="ml-auto h-2 w-2 rounded-full bg-primary" />
          )}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export function ThemeToggleMinimal({ className }: { className?: string }) {
  const { resolvedTheme, setTheme } = useTheme()
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  const toggleTheme = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')
  }

  if (!mounted) {
    return (
      <button
        className={cn(
          'relative h-8 w-14 rounded-full bg-muted p-1 transition-colors',
          className
        )}
      >
        <span className="block h-6 w-6 rounded-full bg-card shadow-soft-sm" />
      </button>
    )
  }

  return (
    <button
      onClick={toggleTheme}
      className={cn(
        'relative h-8 w-14 rounded-full p-1 transition-all duration-300',
        'bg-muted hover:bg-muted/80',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background',
        className
      )}
      aria-label="Toggle theme"
    >
      <span
        className={cn(
          'flex h-6 w-6 items-center justify-center rounded-full bg-card shadow-soft-md transition-all duration-300',
          resolvedTheme === 'dark' ? 'translate-x-6' : 'translate-x-0'
        )}
      >
        {resolvedTheme === 'dark' ? (
          <Moon className="h-3.5 w-3.5 text-foreground" />
        ) : (
          <Sun className="h-3.5 w-3.5 text-foreground" />
        )}
      </span>
    </button>
  )
}
