import { useState, useCallback } from 'react'

interface ModalState {
  isOpen: boolean
  type: 'generate' | 'result' | 'chat' | 'error' | null
  data?: any
}

export function useModal(): {
  isOpen: boolean
  type: ModalState['type']
  data: any
  openModal: (type: ModalState['type'], data?: any) => void
  closeModal: () => void
  switchModal: (newType: ModalState['type'], data?: any) => void
} {
  const [modalState, setModalState] = useState<ModalState>({
    isOpen: false,
    type: null,
    data: null
  })

  const openModal = useCallback((type: ModalState['type'], data?: any) => {
    // Close any existing modal first
    setModalState({ isOpen: false, type: null, data: null })
    
    // Small delay to ensure clean transition
    setTimeout(() => {
      setModalState({ isOpen: true, type, data })
    }, 100)
  }, [])

  const closeModal = useCallback(() => {
    setModalState({ isOpen: false, type: null, data: null })
  }, [])

  const switchModal = useCallback((newType: ModalState['type'], data?: any) => {
    if (modalState.isOpen) {
      // If modal is already open, switch content
      setModalState({ isOpen: true, type: newType, data })
    } else {
      // If no modal is open, open new one
      openModal(newType, data)
    }
  }, [modalState.isOpen, openModal])

  return {
    isOpen: modalState.isOpen,
    type: modalState.type,
    data: modalState.data,
    openModal,
    closeModal,
    switchModal
  }
}
