'use client'

import { useEffect } from 'react'
import { X } from 'lucide-react'
import { useModal } from '@/hooks/useModal'

interface ModalProps {
  children: React.ReactNode
  className?: string
}

export function ModalProvider({ children }: { children: React.ReactNode }): JSX.Element {
  const { isOpen, type, closeModal } = useModal()

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        closeModal()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, closeModal])

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }

    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  return (
    <>
      {children}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={closeModal}
          />
          
          {/* Modal Content */}
          <div className="relative z-10 w-full max-w-lg mx-4">
            <button
              onClick={closeModal}
              className="absolute -top-12 right-0 text-white/60 hover:text-white transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
            
            <div className="anime-card p-6 max-h-[80vh] overflow-y-auto">
              {/* Dynamic content based on modal type */}
              {type === 'generate' && <GenerateModalContent />}
              {type === 'result' && <ResultModalContent />}
              {type === 'chat' && <ChatModalContent />}
              {type === 'error' && <ErrorModalContent />}
            </div>
          </div>
        </div>
      )}
    </>
  )
}

function GenerateModalContent(): JSX.Element {
  return (
    <div className="text-center">
      <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center mx-auto mb-4">
        <span className="text-2xl">✨</span>
      </div>
      <h3 className="text-2xl font-bold text-white mb-2">Create Anime Magic</h3>
      <p className="text-gray-300 mb-6">Choose what you want to generate</p>
      
      <div className="space-y-3">
        <button className="w-full glow-button">Generate Story</button>
        <button className="w-full border border-purple-500 text-white px-6 py-3 rounded-lg hover:bg-purple-500/20 transition-all">Create Character</button>
        <button className="w-full border border-purple-500 text-white px-6 py-3 rounded-lg hover:bg-purple-500/20 transition-all">Animate Scene</button>
      </div>
    </div>
  )
}

function ResultModalContent(): JSX.Element {
  return (
    <div className="text-center">
      <div className="w-16 h-16 bg-gradient-to-r from-green-600 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
        <span className="text-2xl">🎉</span>
      </div>
      <h3 className="text-2xl font-bold text-white mb-2">Creation Complete!</h3>
      <p className="text-gray-300 mb-6">Your anime content has been generated successfully</p>
      
      <div className="space-y-3">
        <button className="w-full glow-button">View Result</button>
        <button className="w-full border border-purple-500 text-white px-6 py-3 rounded-lg hover:bg-purple-500/20 transition-all">Create Another</button>
      </div>
    </div>
  )
}

function ChatModalContent(): JSX.Element {
  return (
    <div className="text-center">
      <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
        <span className="text-2xl">💬</span>
      </div>
      <h3 className="text-2xl font-bold text-white mb-2">AI Assistant</h3>
      <p className="text-gray-300 mb-6">Chat with our AI for creative help</p>
      
      <div className="space-y-3">
        <button className="w-full glow-button">Start Chatting</button>
        <button className="w-full border border-purple-500 text-white px-6 py-3 rounded-lg hover:bg-purple-500/20 transition-all">Get Suggestions</button>
      </div>
    </div>
  )
}

function ErrorModalContent(): JSX.Element {
  return (
    <div className="text-center">
      <div className="w-16 h-16 bg-gradient-to-r from-red-600 to-orange-600 rounded-full flex items-center justify-center mx-auto mb-4">
        <span className="text-2xl">⚠️</span>
      </div>
      <h3 className="text-2xl font-bold text-white mb-2">Oops! Something went wrong</h3>
      <p className="text-gray-300 mb-6">Please try again or contact support if the problem persists</p>
      
      <div className="space-y-3">
        <button className="w-full glow-button">Try Again</button>
        <button className="w-full border border-purple-500 text-white px-6 py-3 rounded-lg hover:bg-purple-500/20 transition-all">Go Back</button>
      </div>
    </div>
  )
}

// Hook for easy modal access
export function useModalActions() {
  const { openModal, closeModal, switchModal } = useModal()
  
  return {
    showGenerateModal: () => openModal('generate'),
    showResultModal: () => openModal('result'),
    showChatModal: () => openModal('chat'),
    showErrorModal: () => openModal('error'),
    closeModal,
    switchModal
  }
}
