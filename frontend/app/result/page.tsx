'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Sparkles, ArrowLeft, Download, Share2, Heart, Book, Image, Video, Loader2 } from 'lucide-react'

interface GeneratedContent {
  type: 'story' | 'image' | 'video'
  content: string
  title?: string
  imageUrl?: string
  videoUrl?: string
}

export default function ResultPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [content, setContent] = useState<GeneratedContent | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isLiked, setIsLiked] = useState(false)

  useEffect(() => {
    const type = searchParams.get('type')
    const data = searchParams.get('data')

    if (type && data) {
      try {
        const parsedData = JSON.parse(decodeURIComponent(data))
        setContent({
          type: type as any,
          ...parsedData
        })
      } catch (error) {
        console.error('Error parsing result data:', error)
        router.push('/generate')
      }
    } else {
      router.push('/generate')
    }

    setIsLoading(false)
  }, [router, searchParams])

  const handleShare = async () => {
    if (navigator.share && content) {
      try {
        await navigator.share({
          title: content.title || 'AI Generated Anime',
          text: 'Check out this amazing anime content I created with AI!',
          url: window.location.href
        })
      } catch (error) {
        console.error('Error sharing:', error)
      }
    }
  }

  const handleDownload = () => {
    if (content) {
      const element = document.createElement('a')
      const file = new Blob([content.content], { type: 'text/plain' })
      element.href = URL.createObjectURL(file)
      element.download = `${content.title || 'anime-content'}.txt`
      document.body.appendChild(element)
      element.click()
      document.body.removeChild(element)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-dark via-purple-900/10 to-darker flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-purple-500 animate-spin mx-auto mb-4" />
          <p className="text-white">Loading your creation...</p>
        </div>
      </div>
    )
  }

  if (!content) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-dark via-purple-900/10 to-darker flex items-center justify-center">
        <div className="text-center">
          <p className="text-white mb-4">No content found</p>
          <Link href="/generate" className="glow-button">
            Create New
          </Link>
        </div>
      </div>
    )
  }

  const getTypeIcon = () => {
    switch (content.type) {
      case 'story':
        return Book
      case 'image':
        return Image
      case 'video':
        return Video
      default:
        return Sparkles
    }
  }

  const getTypeColor = () => {
    switch (content.type) {
      case 'story':
        return 'from-purple-600 to-purple-700'
      case 'image':
        return 'from-pink-600 to-pink-700'
      case 'video':
        return 'from-blue-600 to-blue-700'
      default:
        return 'from-purple-600 to-pink-600'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark via-purple-900/10 to-darker">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-dark/80 backdrop-blur-lg border-b border-purple-500/20 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link href="/generate" className="text-white hover:text-purple-400 transition-colors">
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="flex items-center space-x-2">
                <Sparkles className="w-8 h-8 text-purple-500" />
                <span className="text-2xl font-bold gradient-text">AnimeAI</span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setIsLiked(!isLiked)}
                className="p-2 rounded-lg hover:bg-purple-500/20 transition-colors"
              >
                <Heart className={`w-5 h-5 ${isLiked ? 'text-red-500 fill-current' : 'text-white'}`} />
              </button>
              <button
                onClick={handleShare}
                className="p-2 rounded-lg hover:bg-purple-500/20 transition-colors"
              >
                <Share2 className="w-5 h-5 text-white" />
              </button>
              <button
                onClick={handleDownload}
                className="p-2 rounded-lg hover:bg-purple-500/20 transition-colors"
              >
                <Download className="w-5 h-5 text-white" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${getTypeColor()} flex items-center justify-center`}>
                {React.createElement(getTypeIcon(), { className: 'w-6 h-6 text-white' })}
              </div>
              <h1 className="text-3xl md:text-4xl font-bold gradient-text">
                {content.title || 'Your Creation'}
              </h1>
            </div>
            <div className="flex items-center justify-center space-x-4 text-gray-400">
              <span className="capitalize">{content.type}</span>
              <span>•</span>
              <span>Generated by AI</span>
            </div>
          </div>

          {/* Content Display */}
          <div className="anime-card p-8 mb-8">
            {content.type === 'story' && (
              <div className="prose prose-invert max-w-none">
                <div className="whitespace-pre-wrap text-gray-300 leading-relaxed">
                  {content.content}
                </div>
              </div>
            )}

            {content.type === 'image' && (
              <div className="space-y-6">
                {content.imageUrl && (
                  <div className="relative aspect-square rounded-lg overflow-hidden">
                    <img
                      src={content.imageUrl}
                      alt="Generated anime character"
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
                {content.content && (
                  <div className="text-gray-300">
                    <h3 className="text-xl font-semibold text-white mb-3">Character Description</h3>
                    <p className="leading-relaxed">{content.content}</p>
                  </div>
                )}
              </div>
            )}

            {content.type === 'video' && (
              <div className="space-y-6">
                {content.videoUrl && (
                  <div className="relative aspect-video rounded-lg overflow-hidden bg-dark/50">
                    <video
                      src={content.videoUrl}
                      controls
                      className="w-full h-full"
                    />
                  </div>
                )}
                {content.content && (
                  <div className="text-gray-300">
                    <h3 className="text-xl font-semibold text-white mb-3">Scene Description</h3>
                    <p className="leading-relaxed">{content.content}</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <Link href="/generate" className="glow-button text-center">
              <Sparkles className="inline-block w-5 h-5 mr-2" />
              Create Another
            </Link>
            <button
              onClick={handleShare}
              className="border border-purple-500 text-white px-8 py-3 rounded-lg hover:bg-purple-500/20 transition-all duration-300 text-center"
            >
              <Share2 className="inline-block w-5 h-5 mr-2" />
              Share Creation
            </button>
          </div>

          {/* Tips */}
          <div className="anime-card p-6">
            <h3 className="text-lg font-semibold text-white mb-4">🎨 Enhance Your Creation</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <p className="text-gray-300 text-sm">• Save your favorite creations to your library</p>
                <p className="text-gray-300 text-sm">• Share with friends on social media</p>
              </div>
              <div className="space-y-2">
                <p className="text-gray-300 text-sm">• Use different prompts for variations</p>
                <p className="text-gray-300 text-sm">• Combine multiple creations for stories</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
