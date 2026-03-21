import { NextResponse } from 'next/server'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/chat/suggestions`)
    
    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Chat suggestions API error:', error)
    return NextResponse.json(
      { 
        success: false, 
        conversation_starters: [
          'मैं एक एनीमे कहानी बनाना चाहता हूं',
          'मुझे एक एनीमे कैरेक्टर बनाने में मदद चाहिए',
          'क्या आप मेरे लिए एक एनीमे वीडियो बना सकते हैं?'
        ]
      },
      { status: 500 }
    )
  }
}
