import { NextRequest, NextResponse } from 'next/server'
import { firebaseService } from '@/services/firebaseService'

export async function POST(request: NextRequest) {
  try {
    const { collection, data, docId } = await request.json()

    if (!collection || !data) {
      return NextResponse.json(
        { error: 'Collection and data are required' },
        { status: 400 }
      )
    }

    const savedId = await firebaseService.saveToFirestore(collection, data, docId)
    
    return NextResponse.json({
      success: true,
      id: savedId,
      message: 'Data saved successfully'
    })
  } catch (error) {
    console.error('Firebase save error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to save data to Firestore'
      },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const collection = searchParams.get('collection')
    const docId = searchParams.get('docId')
    const limit = parseInt(searchParams.get('limit') || '10')

    if (!collection) {
      return NextResponse.json(
        { error: 'Collection is required' },
        { status: 400 }
      )
    }

    if (docId) {
      // Get specific document
      const data = await firebaseService.getFromFirestore(collection, docId)
      return NextResponse.json({
        success: true,
        data
      })
    } else {
      // Query collection
      const data = await firebaseService.queryFirestore(collection, limit)
      return NextResponse.json({
        success: true,
        data
      })
    }
  } catch (error) {
    console.error('Firebase query error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to query Firestore'
      },
      { status: 500 }
    )
  }
}
