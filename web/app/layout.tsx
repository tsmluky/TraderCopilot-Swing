import React from 'react'
import type { Metadata, Viewport } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import { ThemeProvider } from '@/components/theme-provider'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-sans',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-mono',
})

export const metadata: Metadata = {
  title: {
    default: 'TraderCopilot Swing',
    template: '%s | TraderCopilot Swing',
  },
  description: 'Institutional-grade swing trading signals for BTC, ETH, SOL, BNB, and XRP. AI-powered analysis with professional execution guidance.',
  generator: 'TraderCopilot',
  keywords: ['crypto', 'swing trading', 'trading signals', 'bitcoin', 'ethereum', 'institutional'],
  authors: [{ name: 'TraderCopilot' }],
  openGraph: {
    title: 'TraderCopilot — Swing',
    description: 'Institutional-grade swing trading signals',
    type: 'website',
  },
}

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#09090b' },
  ],
  colorScheme: 'dark light',
  width: 'device-width',
  initialScale: 1,
}

import { AuthProvider } from '@/context/auth-context'
import { Toaster } from '@/components/ui/sonner'

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${inter.variable} ${jetbrainsMono.variable}`}
    >
      <body className="font-sans antialiased min-h-screen bg-background text-foreground">
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange={false}
        >
          <AuthProvider>
            {children}
            <Toaster />
          </AuthProvider>
        </ThemeProvider>
        <Analytics />
      </body>
    </html>
  )
}
