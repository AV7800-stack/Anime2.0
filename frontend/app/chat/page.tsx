'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Sparkles, ArrowLeft, Send, Bot, User, Lightbulb } from 'lucide-react'
import axios from 'axios'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  suggestions?: string[]
}

export default function ChatPage() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [conversationStarters, setConversationStarters] = useState<string[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Load conversation starters
    loadConversationStarters()
    
    // Add welcome message
    const welcomeMessage: Message = {
      id: '1',
      role: 'assistant',
      content: 'नमस्ते! मैं आपका AI Anime Assistant हूं। मैं आपको एनीमे कहानियां, कैरेक्टर्स, और वीडियो बनाने में मदद कर सकता हूं।\n\nआप क्या बनाना चाहते हैं? 🎨✨',
      timestamp: new Date().toISOString()
    }
    setMessages([welcomeMessage])
  }, [])

  const loadConversationStarters = async () => {
    try {
      const response = await axios.get('/api/chat/suggestions')
      if (response.data.success) {
        setConversationStarters(response.data.conversation_starters)
      }
    } catch (error) {
      console.error('Failed to load conversation starters:', error)
    }
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await axios.post('/api/chat', {
        message: inputMessage,
        conversation_history: messages.map(msg => ({
          role: msg.role,
          content: msg.content
        }))
      })

      if (response.data.success) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.data.response,
          timestamp: response.data.timestamp,
          suggestions: response.data.suggestions
        }

        setMessages(prev => [...prev, assistantMessage])
        setSuggestions(response.data.suggestions || [])
      }
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'मुझे अभी बात नहीं कर सकता, कृपया थोड़ी देर बाद फिर कोशिश करें।',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion)
    inputRef.current?.focus()
  }

  const handleStarterClick = (starter: string) => {
    setInputMessage(starter)
    inputRef.current?.focus()
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark via-purple-900/10 to-darker">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-dark/80 backdrop-blur-lg border-b border-purple-500/20 z-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-white hover:text-purple-400 transition-colors">
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="flex items-center space-x-2">
                <Sparkles className="w-8 h-8 text-purple-500" />
                <span className="text-2xl font-bold gradient-text">AnimeAI Chat</span>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Bot className="w-5 h-5 text-green-400" />
              <span className="text-green-400 text-sm">Online</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Chat Area */}
      <div className="pt-20 pb-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Messages */}
          <div className="space-y-4 mb-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-2xl ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                      : 'anime-card text-gray-300'
                  } rounded-2xl px-6 py-4 shadow-lg`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      {message.role === 'user' ? (
                        <User className="w-5 h-5 text-white" />
                      ) : (
                        <Bot className="w-5 h-5 text-purple-400" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="whitespace-pre-wrap text-sm leading-relaxed">
                        {message.content}
                      </p>
                      {message.suggestions && message.suggestions.length > 0 && (
                        <div className="mt-3 space-y-2">
                          <p className="text-xs font-semibold flex items-center space-x-1">
                            <Lightbulb className="w-3 h-3" />
                            <span>सुझाव:</span>
                          </p>
                          <div className="space-y-1">
                            {message.suggestions.map((suggestion, index) => (
                              <button
                                key={index}
                                onClick={() => handleSuggestionClick(suggestion)}
                                className="block w-full text-left text-xs bg-purple-500/20 hover:bg-purple-500/30 px-3 py-2 rounded-lg transition-colors"
                              >
                                {suggestion}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="anime-card rounded-2xl px-6 py-4 shadow-lg">
                  <div className="flex items-center space-x-3">
                    <Bot className="w-5 h-5 text-purple-400" />
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Conversation Starters (only show when no messages beyond welcome) */}
          {messages.length <= 1 && !isLoading && (
            <div className="anime-card p-6 mb-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                <Lightbulb className="w-5 h-5 text-yellow-400" />
                <span>बातचीत शुरू करने के लिए आइडिया:</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {conversationStarters.map((starter, index) => (
                  <button
                    key={index}
                    onClick={() => handleStarterClick(starter)}
                    className="text-left bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 px-4 py-3 rounded-lg transition-colors text-sm"
                  >
                    {starter}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="fixed bottom-0 w-full bg-dark/90 backdrop-blur-lg border-t border-purple-500/20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center space-x-4">
            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="अपना संदेश यहां लिखें..."
              className="flex-1 bg-dark/50 border border-purple-500/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all duration-300"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="glow-button p-3 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          
          {/* Quick suggestions */}
          {suggestions.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="text-xs bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 px-3 py-1 rounded-full transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
