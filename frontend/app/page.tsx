'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Sparkles, Play, Plus, Star, TrendingUp, Clock, Bot } from 'lucide-react'
import { useModalActions } from '@/components/Modal'

export default function HomePage() {
  const [featuredAnime] = useState([
    {
      id: 1,
      title: "Magical Girl Academy",
      description: "A young girl discovers her hidden powers and joins an academy for magical warriors.",
      image: "/api/placeholder/300/450",
      rating: 4.8,
      genre: "Fantasy",
      trending: true
    },
    {
      id: 2,
      title: "Cyber Samurai",
      description: "In a dystopian future, a samurai warrior fights against corrupt AI overlords.",
      image: "/api/placeholder/300/450",
      rating: 4.6,
      genre: "Sci-Fi",
      trending: true
    },
    {
      id: 3,
      title: "Love in Tokyo",
      description: "A heartwarming romance between two high school students in modern Tokyo.",
      image: "/api/placeholder/300/450",
      rating: 4.9,
      genre: "Romance",
      trending: false
    }
  ])

  const { showGenerateModal, showChatModal } = useModalActions()

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark via-purple-900/10 to-darker">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-dark/80 backdrop-blur-lg border-b border-purple-500/20 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-8 h-8 text-purple-500" />
              <span className="text-2xl font-bold gradient-text">AnimeAI</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <Link href="/" className="text-white hover:text-purple-400 transition-colors">Home</Link>
              <Link href="/generate" className="text-white hover:text-purple-400 transition-colors">Generate</Link>
              <Link href="/chat" className="text-white hover:text-purple-400 transition-colors flex items-center space-x-1">
                <Bot className="w-4 h-4" />
                <span>Chat</span>
              </Link>
              <Link href="/library" className="text-white hover:text-purple-400 transition-colors">Library</Link>
            </div>
            <Link 
              href="/generate" 
              className="glow-button flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>Create New</span>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="gradient-text">AI-Powered Anime</span>
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Create stunning anime stories, characters, and worlds with the power of artificial intelligence. 
            Bring your imagination to life in seconds.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/generate" className="glow-button text-lg px-8 py-4">
              <Sparkles className="inline-block w-5 h-5 mr-2" />
              Generate Anime Now
            </Link>
            <button className="border border-purple-500 text-white px-8 py-4 rounded-lg hover:bg-purple-500/20 transition-all duration-300">
              <Play className="inline-block w-5 h-5 mr-2" />
              Watch Demo
            </button>
          </div>
        </div>
      </section>

      {/* Featured Anime */}
      <section className="py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-3">
              <TrendingUp className="w-6 h-6 text-purple-500" />
              <h2 className="text-3xl font-bold text-white">Featured Creations</h2>
            </div>
            <button className="text-purple-400 hover:text-purple-300 transition-colors">
              View All →
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredAnime.map((anime) => (
              <div key={anime.id} className="anime-card group cursor-pointer">
                <div className="relative aspect-[2/3] mb-4 overflow-hidden rounded-lg">
                  <div className="w-full h-full bg-gradient-to-br from-purple-600 to-pink-600 opacity-50"></div>
                  {anime.trending && (
                    <div className="absolute top-2 right-2 bg-red-600 text-white text-xs px-2 py-1 rounded-full flex items-center space-x-1">
                      <TrendingUp className="w-3 h-3" />
                      <span>Trending</span>
                    </div>
                  )}
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                    <Play className="w-12 h-12 text-white" />
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{anime.title}</h3>
                <p className="text-gray-400 text-sm mb-3 line-clamp-2">{anime.description}</p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Star className="w-4 h-4 text-yellow-500 fill-current" />
                    <span className="text-white text-sm">{anime.rating}</span>
                  </div>
                  <span className="text-purple-400 text-sm">{anime.genre}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">Why Choose AnimeAI?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="anime-card text-center">
              <Sparkles className="w-12 h-12 text-purple-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">AI-Powered Stories</h3>
              <p className="text-gray-400">Generate unique anime plots with advanced AI technology</p>
            </div>
            <div className="anime-card text-center">
              <Play className="w-12 h-12 text-pink-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Character Design</h3>
              <p className="text-gray-400">Create stunning anime characters with detailed descriptions</p>
            </div>
            <div className="anime-card text-center">
              <Clock className="w-12 h-12 text-blue-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Instant Results</h3>
              <p className="text-gray-400">Get your anime content generated in seconds, not hours</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-purple-500/20 py-8 px-4 sm:px-6 lg:px-8 mt-16">
        <div className="max-w-7xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Sparkles className="w-6 h-6 text-purple-500" />
            <span className="text-xl font-bold gradient-text">AnimeAI</span>
          </div>
          <p className="text-gray-400">© 2024 AnimeAI. Create your dream anime with AI.</p>
        </div>
      </footer>
    </div>
  )
}
