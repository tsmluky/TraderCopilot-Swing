import { Terminal } from 'lucide-react'
import { cn } from '@/lib/utils'

interface BrandLogoProps {
    className?: string
    textSize?: string
    showText?: boolean
    iconSize?: string
    iconColor?: string
}

export function BrandLogo({
    className,
    textSize = "text-sm",
    showText = true,
    iconSize = "h-8 w-8",
    iconColor = "text-primary"
}: BrandLogoProps) {
    return (
        <div className={cn("flex items-center gap-3 group", className)}>
            <div className="relative">
                {/* Glow Effect */}
                <div className="absolute inset-0 bg-primary/20 rounded-lg blur opacity-0 group-hover:opacity-100 transition-opacity" />

                {/* Icon Container */}
                <div className={cn("relative flex items-center justify-center rounded-lg bg-white/5 border border-white/10", iconSize)}>
                    <Terminal className={cn("h-4 w-4", iconColor)} />
                </div>
            </div>

            {/* Brand Text */}
            {showText && (
                <span className={cn("font-semibold tracking-tight text-foreground", textSize)}>
                    TraderCopilot
                </span>
            )}
        </div>
    )
}
