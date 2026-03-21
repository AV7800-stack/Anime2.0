import { NextRequest, NextResponse } from 'next/server'
import { firebaseService } from '@/services/firebaseService'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    const path = formData.get('path') as string

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      )
    }

    const downloadUrl = await firebaseService.uploadToStorage(file, path)
    
    return NextResponse.json({
      success: true,
      url: downloadUrl,
      message: 'File uploaded successfully'
    })
  } catch (error) {
    console.error('Firebase upload error:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to upload file to Firebase Storage'
      },
      { status: 500 }
    )
  }
}
