'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Sparkles, ArrowLeft, Wand2, Image, Video, Book, Loader2 } from 'lucide-react'
import axios from 'axios'

export default function GeneratePage() {
  const router = useRouter()
  const [prompt, setPrompt] = useState('')
  const [selectedType, setSelectedType] = useState<'story' | 'image' | 'video'>('story')
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    setIsGenerating(true)
    setError('')

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      let response

      switch (selectedType) {
        case 'story':
          response = await axios.post(`${apiUrl}/generate-story`, {
            prompt: prompt.trim()
          })
          break
        case 'image':
          response = await axios.post(`${apiUrl}/generate-image`, {
            prompt: prompt.trim()
          })
          break
        case 'video':
          response = await axios.post(`${apiUrl}/generate-video`, {
            prompt: prompt.trim()
          })
          break
      }

      // Navigate to results page with the generated content
      router.push(`/result?type=${selectedType}&data=${encodeURIComponent(JSON.stringify(response.data))}`)
    } catch (err) {
      console.error('Generation error:', err)
      setError('Failed to generate content. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  const generationTypes = [
    {
      id: 'story',
      title: 'Anime Story',
      description: 'Generate a complete anime story with characters and plot',
      icon: Book,
      color: 'from-purple-600 to-purple-700'
    },
    {
      id: 'image',
      title: 'Anime Character',
      description: 'Create stunning anime character images',
      icon: Image,
      color: 'from-pink-600 to-pink-700'
    },
    {
      id: 'video',
      title: 'Anime Scene',
      description: 'Generate animated anime scenes',
      icon: Video,
      color: 'from-blue-600 to-blue-700'
    }
  ]

  const examplePrompts = [
    "A shy high school girl discovers she can control time",
    "In a cyberpunk Tokyo, a detective hunts android criminals",
    "A magical academy where students learn elemental spells",
    "A romance between a human and a fox spirit",
    "Space pirates searching for ancient alien artifacts"
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark via-purple-900/10 to-darker">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-dark/80 backdrop-blur-lg border-b border-purple-500/20 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-white hover:text-purple-400 transition-colors">
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="flex items-center space-x-2">
                <Sparkles className="w-8 h-8 text-purple-500" />
                <span className="text-2xl font-bold gradient-text">AnimeAI</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="gradient-text">Create Your Anime</span>
            </h1>
            <p className="text-xl text-gray-300">
              Describe your idea and let AI bring it to life
            </p>
          </div>

          {/* Generation Type Selection */}
          <div className="mb-8">
            <h2 className="text-2xl font-semibold text-white mb-6">What would you like to create?</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {generationTypes.map((type) => {
                const Icon = type.icon
                return (
                  <button
                    key={type.id}
                    onClick={() => setSelectedType(type.id as any)}
                    className={`anime-card p-6 text-left transition-all duration-300 ${
                      selectedType === type.id
                        ? 'border-purple-500 shadow-lg shadow-purple-500/20'
                        : 'hover:border-purple-500/40'
                    }`}
                  >
                    <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${type.color} flex items-center justify-center mb-4`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-lg font-semibold text-white mb-2">{type.title}</h3>
                    <p className="text-gray-400 text-sm">{type.description}</p>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Prompt Input */}
          <div className="anime-card p-8 mb-8">
            <label htmlFor="prompt" className="block text-lg font-semibold text-white mb-4">
              Describe your anime idea
            </label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter your creative idea here. For example: 'A magical girl who fights demons with the power of music in modern Tokyo...'"
              className="w-full h-32 bg-dark/50 border border-purple-500/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all duration-300 resize-none"
            />
            
            {/* Example Prompts */}
            <div className="mt-4">
              <p className="text-sm text-gray-400 mb-2">Need inspiration? Try these:</p>
              <div className="flex flex-wrap gap-2">
                {examplePrompts.map((example, index) => (
                  <button
                    key={index}
                    onClick={() => setPrompt(example)}
                    className="text-xs bg-purple-500/20 text-purple-300 px-3 py-1 rounded-full hover:bg-purple-500/30 transition-colors"
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-500/20 border border-red-500/50 text-red-300 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {/* Generate Button */}
          <div className="text-center">
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !prompt.trim()}
              className="glow-button text-lg px-12 py-4 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="inline-block w-5 h-5 mr-2 animate-spin" />
                  Generating Magic...
                </>
              ) : (
                <>
                  <Wand2 className="inline-block w-5 h-5 mr-2" />
                  Generate {generationTypes.find(t => t.id === selectedType)?.title}
                </>
              )}
            </button>
          </div>

          {/* Tips */}
          <div className="mt-12 anime-card p-6">
            <h3 className="text-lg font-semibold text-white mb-4">✨ Pro Tips</h3>
            <ul className="space-y-2 text-gray-300">
              <li className="flex items-start">
                <span className="text-purple-400 mr-2">•</span>
                Be specific about characters, setting, and mood for better results
              </li>
              <li className="flex items-start">
                <span className="text-purple-400 mr-2">•</span>
                Include details about art style (e.g., 'Studio Ghibli style', 'shonen manga style')
              </li>
              <li className="flex items-start">
                <span className="text-purple-400 mr-2">•</span>
                Mention emotions and actions to create more dynamic content
              </li>
              <li className="flex items-start">
                <span className="text-purple-400 mr-2">•</span>
                Combine genres for unique results (e.g., 'sci-fi romance', 'fantasy horror')
              </li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  )
}
