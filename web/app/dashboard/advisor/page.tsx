'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Sparkles } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'
import { useAuth } from '@/context/auth-context'
import { AdvisorLocked } from '@/components/advisor-locked'
import { advisorService } from '@/services/advisor'
import { toast } from 'sonner'

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

export default function AdvisorPage() {
  const { canAccessAdvisor, user } = useAuth()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: `Hello ${user?.name?.split(' ')[0] || 'Trader'}! I'm your AI Swing Trading Advisor. I can help you with:

- Market analysis and sentiment
- Trade setup evaluation
- Risk management guidance
- Technical analysis insights

What would you like to discuss today?`,
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
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

      const response: any = await advisorService.chat(history)

      // Backend returns { reply, usage }.
      // Keep backwards compatibility with older shapes: response/message/content/text.
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
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            AI Advisor
            <Badge className="bg-primary/10 text-primary border-primary/30 text-xs">
              <Sparkles className="h-3 w-3 mr-1" />
              PRO
            </Badge>
          </h1>
          <p className="text-muted-foreground">
            Get personalized swing trading insights powered by AI
          </p>
        </div>
      </div>

      <Card className="flex flex-1 flex-col bg-card border-border overflow-hidden">
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  'flex gap-3',
                  message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                )}
              >
                <Avatar
                  className={cn(
                    'h-8 w-8 shrink-0',
                    message.role === 'assistant' ? 'bg-primary/10' : 'bg-secondary'
                  )}
                >
                  <AvatarFallback
                    className={cn(
                      'text-xs',
                      message.role === 'assistant'
                        ? 'text-primary'
                        : 'text-foreground'
                    )}
                  >
                    {message.role === 'assistant'
                      ? 'AI'
                      : user?.name?.charAt(0) || 'U'}
                  </AvatarFallback>
                </Avatar>
                <div
                  className={cn(
                    'max-w-[75%] rounded-lg px-4 py-3',
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary/50'
                  )}
                >
                  <div
                    className={cn(
                      'text-sm whitespace-pre-wrap prose prose-sm max-w-none',
                      message.role === 'user'
                        ? 'text-primary-foreground prose-invert'
                        : 'text-foreground dark:prose-invert'
                    )}
                  >
                    {message.content.split('\n').map((line, i) => {
                      if (line.startsWith('**') && line.endsWith('**')) {
                        return (
                          <p key={i} className="font-semibold mt-2 first:mt-0">
                            {line.slice(2, -2)}
                          </p>
                        )
                      }
                      if (line.startsWith('- ')) {
                        return (
                          <p key={i} className="ml-2">
                            {line}
                          </p>
                        )
                      }
                      return <p key={i}>{line}</p>
                    })}
                  </div>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex gap-3">
                <Avatar className="h-8 w-8 bg-primary/10">
                  <AvatarFallback className="text-xs text-primary">
                    AI
                  </AvatarFallback>
                </Avatar>
                <div className="rounded-lg bg-secondary/50 px-4 py-3">
                  <div className="flex gap-1">
                    <span
                      className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce"
                      style={{ animationDelay: '0ms' }}
                    />
                    <span
                      className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce"
                      style={{ animationDelay: '150ms' }}
                    />
                    <span
                      className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce"
                      style={{ animationDelay: '300ms' }}
                    />
                  </div>
                </div>
              </div>
            )}
            )}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {messages.length === 1 && (
          <div className="border-t border-border p-4">
            <p className="text-xs text-muted-foreground mb-2">
              Suggested questions:
            </p>
            <div className="flex flex-wrap gap-2">
              {suggestedQuestions.map((question, i) => (
                <Button
                  key={i}
                  variant="outline"
                  size="sm"
                  className="text-xs h-7 bg-transparent"
                  onClick={() => handleSuggestedQuestion(question)}
                >
                  {question}
                </Button>
              ))}
            </div>
          </div>
        )}

        <div className="border-t border-border p-4">
          <form
            onSubmit={(e) => {
              e.preventDefault()
              handleSend()
            }}
            className="flex gap-2"
          >
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about market analysis, trade setups, or strategies..."
              className="flex-1 bg-secondary/30 border-border"
              disabled={isTyping}
            />
            <Button type="submit" disabled={!input.trim() || isTyping}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </Card>
    </div>
  )
}
