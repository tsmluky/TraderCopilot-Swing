'use client'

import { TrendingUp, TrendingDown, Lock } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { useUser } from '@/lib/user-context'
import { tokenPrices, formatPrice, formatPercent, TOKEN_INFO } from '@/lib/mock-data'
import type { Token } from '@/lib/types'

export function TokenPrices() {
  const { canAccessToken } = useUser()
  const tokens = Object.keys(tokenPrices) as Token[]

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <CardTitle className="text-base font-medium">Market Overview</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {tokens.map((token) => {
          const price = tokenPrices[token]
          const info = TOKEN_INFO[token]
          const isLocked = !canAccessToken(token)
          const isPositive = price.change24h >= 0

          return (
            <div
              key={token}
              className={cn(
                'flex items-center justify-between rounded-lg p-3 transition-colors',
                isLocked ? 'bg-muted/30 opacity-50' : 'bg-secondary/30 hover:bg-secondary/50'
              )}
            >
              <div className="flex items-center gap-3">
                <div
                  className="h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold"
                  style={{ backgroundColor: `${info.color}20`, color: info.color }}
                >
                  {token}
                </div>
                <div>
                  <p className="font-medium text-foreground text-sm">{token}</p>
                  <p className="text-xs text-muted-foreground">{info.name}</p>
                </div>
              </div>
              
              {isLocked ? (
                <div className="flex items-center gap-1 text-muted-foreground">
                  <Lock className="h-3.5 w-3.5" />
                  <span className="text-xs">Locked</span>
                </div>
              ) : (
                <div className="text-right">
                  <p className="font-mono text-sm font-medium text-foreground">
                    ${formatPrice(price.price)}
                  </p>
                  <div
                    className={cn(
                      'flex items-center justify-end gap-1 text-xs',
                      isPositive ? 'text-success' : 'text-destructive'
                    )}
                  >
                    {isPositive ? (
                      <TrendingUp className="h-3 w-3" />
                    ) : (
                      <TrendingDown className="h-3 w-3" />
                    )}
                    {formatPercent(price.change24h)}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
