'use client'

import { TrendingUp, TrendingDown, Lock } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { useUser } from '@/lib/user-context'
import { TOKEN_INFO } from '@/lib/types'
import { formatPrice, formatPercent } from '@/lib/formatters'
import type { Token } from '@/lib/types'
import { marketService } from '@/services/market'
import { useEffect, useState } from 'react'

export function TokenPrices() {
  const { canAccessToken } = useUser()
  const [prices, setPrices] = useState<any[]>([])

  useEffect(() => {
    const fetchPrices = async () => {
      try {
        const syms = Object.keys(TOKEN_INFO)
        const data = await marketService.getMarketSummary(syms)
        if (data && Array.isArray(data)) {
          setPrices(data)
        }
      } catch (e) {
        console.error("Failed to load market summary", e)
      }
    }
    fetchPrices()
    const interval = setInterval(fetchPrices, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  // If loading empty, maybe show skeleton? or just blank.
  const displayList = prices.length > 0 ? prices : Object.keys(TOKEN_INFO).map(t => ({
    symbol: t,
    price: 0,
    change_24h: 0
  }))

  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-3">
        <CardTitle className="text-base font-medium">Market Overview</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {displayList.map((item) => {
          const token = item.symbol as Token
          const info = TOKEN_INFO[token] || { name: token, color: '#888' }
          const isLocked = !canAccessToken(token)
          const isPositive = (item.change_24h || 0) >= 0

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
                    ${formatPrice(item.price || 0)}
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
                    {formatPercent(item.change_24h || 0)}
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
