'use client'

import { useState, useRef, useEffect, Suspense } from 'react'
import { Send, Sparkles, Bot, User, Terminal, X } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'
import { useAuth } from '@/context/auth-context'
import { AdvisorLocked } from '@/components/advisor-locked'
import { advisorService } from '@/services/advisor'
import { signalsService } from '@/services/signals'
import { toast } from 'sonner'
import { useSearchParams } from 'next/navigation'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const suggestedQuestions = [
  'What is the current market sentiment for BTC?',
  'Should I take profit on my ETH long position?',
  'Analyze the SOL/USDT 4H chart setup',
  'What are the key support levels for BNB?',
]

// Componente hijo para manejar params con Suspense
function AdvisorContextManager({ onSignalDetected }: { onSignalDetected: (sig: any) => void }) {
  const searchParams = useSearchParams()
  const signalId = searchParams.get('signalId')

  useEffect(() => {
    if (signalId) {
      const fetchContext = async () => {
        try {
          const sig = await signalsService.getById(signalId)
          if (sig) {
            onSignalDetected(sig)
          }
        } catch (e) {
          console.error("Failed to fetch context signal", e)
          toast.error("Could not load signal context")
        }
      }
      fetchContext()
    }
  }, [signalId, onSignalDetected])

  return null
}

function AdvisorContent() {
  const { canAccessAdvisor, user } = useAuth()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: `Hello ${user?.name?.split(' ')[0] || 'Trader'}! I'm your AI Swing Trading Advisor. \n\nI can help you with:\n- Market analysis and sentiment\n- Trade setup evaluation\n- Risk management guidance\n- Technical analysis insights\n\nWhat would you like to discuss today?`,
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const [activeSignal, setActiveSignal] = useState<any>(null)

  const handleSignalDetected = (sig: any) => {
    setActiveSignal(sig)
    setMessages(prev => {
      const hasContextGreeting = prev.some(m => m.id === 'context-greeting')
      if (hasContextGreeting) return prev

      return [
        ...prev,
        {
          id: 'context-greeting',
          role: 'assistant',
          content: `I see you want to discuss the **${sig.token} ${sig.type}** signal.\n\nEntry: $${sig.entryPrice} | Target: $${sig.targetPrice}\n\nHow can I assist you with this setup?`,
          timestamp: new Date()
        }
      ]
    })
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  const handleSend = async (textOverride?: string) => {
    const text = textOverride || input
    if (!text.trim() || isTyping) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    try {
      const history = [...messages, userMessage].map((m) => ({
        role: m.role,
        content: m.content,
      }))

      // Inject Context if active
      const contextPayload = activeSignal ? {
        token: activeSignal.token,
        timeframe: activeSignal.timeframe,
        signal_data: activeSignal
      } : undefined

      const response: any = await advisorService.chat(history, contextPayload)

      const assistantContent =
        typeof response === 'string'
          ? response
          : response?.reply ||
          response?.response ||
          response?.message ||
          response?.content ||
          response?.text ||
          "I'm sorry, I couldn't process that."

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: assistantContent,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error(error)
      toast.error('Failed to get response from Advisor')
    } finally {
      setIsTyping(false)
    }
  }

  const handleSuggestedQuestion = (question: string) => {
    handleSend(question)
  }

  if (!canAccessAdvisor) {
    return <AdvisorLocked />
  }

  return (
    <div className="flex h-[calc(100vh-100px)] flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">

      {/* Suspense Wrapper for SearchParams */}
      <Suspense fallback={null}>
        <AdvisorContextManager onSignalDetected={handleSignalDetected} />
      </Suspense>

      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
            <span className="bg-gradient-to-r from-indigo-500 to-cyan-500 dark:from-indigo-400 dark:to-cyan-400 bg-clip-text text-transparent">AI Advisor</span>
            <Badge className="bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-indigo-500/20 text-xs px-2 py-0.5 shadow-[0_0_10px_rgba(99,102,241,0.2)]">
              <Sparkles className="h-3 w-3 mr-1" />
              INTELLIGENCE
            </Badge>
          </h1>
          <p className="text-muted-foreground/80 mt-1 font-light">
            Your personal institutional-grade trading analyst.
          </p>
          {activeSignal && (
            <div className="mt-3 inline-flex items-center gap-2 rounded-full border border-indigo-500/20 bg-indigo-500/10 px-3 py-1 text-xs font-medium text-indigo-500 animate-in fade-in slide-in-from-left-4 duration-500">
              <div className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-pulse" />
              Analyzing Signal: {activeSignal.token} {activeSignal.type} (${activeSignal.entryPrice})
              <button onClick={() => setActiveSignal(null)} className="ml-2 hover:text-foreground">
                <X className="h-3 w-3" />
              </button>
            </div>
          )}
        </div>
      </div>

      <Card className="flex flex-1 flex-col bg-white/60 dark:bg-black/20 backdrop-blur-xl border-black/5 dark:border-white/5 overflow-hidden rounded-3xl shadow-2xl relative">
        {/* Background ambience */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-32 bg-indigo-500/5 blur-[100px] pointer-events-none" />

        <div className="flex-1 overflow-y-auto p-6 scroll-smooth space-y-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                'flex gap-4 max-w-3xl animate-in fade-in slide-in-from-bottom-2 duration-300',
                message.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'
              )}
            >
              <div className={cn(
                "h-10 w-10 shrink-0 rounded-xl flex items-center justify-center shadow-lg border border-black/5 dark:border-white/5",
                message.role === 'assistant' ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-500' : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400'
              )}>
                {message.role === 'assistant' ? <Terminal className="w-5 h-5" /> : <User className="w-5 h-5" />}
              </div>

              <div
                className={cn(
                  'rounded-2xl px-6 py-4 shadow-md text-sm leading-relaxed',
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-indigo-600 to-blue-700 text-white rounded-tr-sm'
                    : 'bg-white dark:bg-white/5 border border-black/5 dark:border-white/5 text-foreground rounded-tl-sm backdrop-blur-sm'
                )}
              >
                <div className={cn('whitespace-pre-wrap', message.role === 'user' ? 'text-white/95' : 'text-foreground dark:text-zinc-200')}>
                  {message.content.split('\n').map((line, i) => {
                    // Simple bold handling
                    if (line.includes('**')) {
                      const parts = line.split('**');
                      return (
                        <p key={i} className="mb-2 last:mb-0">
                          {parts.map((part, idx) => (
                            idx % 2 === 1 ? <span key={idx} className={cn("font-bold", message.role === 'user' ? "text-white" : "text-foreground")}>{part}</span> : part
                          ))}
                        </p>
                      )
                    }
                    if (line.startsWith('- ')) {
                      return (
                        <div key={i} className="flex gap-2 ml-1 mb-1 last:mb-0">
                          <span className="text-indigo-400">•</span>
                          <p>{line.substring(2)}</p>
                        </div>
                      )
                    }
                    return <p key={i} className="mb-2 last:mb-0">{line}</p>
                  })}
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex gap-4 max-w-3xl mr-auto animate-pulse">
              <div className="h-10 w-10 shrink-0 rounded-xl flex items-center justify-center shadow-lg border border-black/5 dark:border-white/5 bg-emerald-500/10 text-emerald-600 dark:text-emerald-500">
                <Terminal className="w-5 h-5" />
              </div>
              <div className="rounded-2xl px-6 py-4 bg-white dark:bg-white/5 border border-black/5 dark:border-white/5 rounded-tl-sm backdrop-blur-sm flex items-center gap-1.5 h-[52px]">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} className="h-4" />
        </div>

        {/* Input Area */}
        <div className="p-4 pt-0 relative z-10">
          {messages.length === 1 && !isTyping && (
            <div className="flex flex-wrap gap-2 mb-4 justify-center">
              {suggestedQuestions.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSuggestedQuestion(q)}
                  className="text-xs bg-white/60 dark:bg-white/5 hover:bg-white/80 dark:hover:bg-white/10 border border-black/5 dark:border-white/5 hover:border-indigo-500/30 text-muted-foreground hover:text-indigo-600 dark:hover:text-indigo-300 px-4 py-2 rounded-full transition-all duration-300 transform hover:scale-105 shadow-sm dark:shadow-none"
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          <form
            onSubmit={(e) => {
              e.preventDefault()
              handleSend()
            }}
            className="flex gap-3 items-end p-2 rounded-[2rem] bg-white/80 dark:bg-black/40 border border-black/5 dark:border-white/10 backdrop-blur-xl transition-all focus-within:ring-1 focus-within:ring-indigo-500/50 focus-within:border-indigo-500/50 shadow-lg dark:shadow-none"
          >
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about the market..."
              className="flex-1 bg-transparent border-0 focus-visible:ring-0 text-base py-3 px-4 h-auto placeholder:text-muted-foreground/50 rounded-full text-foreground"
              disabled={isTyping}
            />
            <Button
              type="submit"
              disabled={!input.trim() || isTyping}
              size="icon"
              className="h-10 w-10 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white shadow-[0_0_15px_rgba(79,70,229,0.4)] mr-1 mb-1 transition-all"
            >
              <Send className="h-5 w-5 ml-0.5" />
            </Button>
          </form>
          <div className="text-[10px] text-center text-muted-foreground/30 mt-2">
            AI can make mistakes. Consider checking important information.
          </div>
        </div>
      </Card>
    </div>
  )
}

export default function AdvisorPage() {
  return (
    <Suspense fallback={<div>Loading Advisor...</div>}>
      <AdvisorContent />
    </Suspense>
  )
}
