import { firebaseConfig, firebaseApiKey } from '@/firebase-config'

class FirebaseService {
  private apiKey: string
  private projectId: string
  private storageBucket: string

  constructor() {
    this.apiKey = firebaseApiKey
    this.projectId = firebaseConfig.project_info.project_id
    this.storageBucket = firebaseConfig.project_info.storage_bucket
  }

  // Firebase Storage for image/video uploads
  async uploadToStorage(file: File, path: string): Promise<string> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('path', path)

      const response = await fetch(
        `https://firebasestorage.googleapis.com/v0/b/${this.storageBucket}/o?uploadType=media&name=${path}`,
        {
          method: 'POST',
          body: formData,
          headers: {
            'Authorization': `Bearer ${this.apiKey}`
          }
        }
      )

      if (!response.ok) {
        throw new Error('Failed to upload to Firebase Storage')
      }

      const data = await response.json()
      return `https://firebasestorage.googleapis.com/v0/b/${this.storageBucket}/o/${encodeURIComponent(path)}?alt=media`
    } catch (error) {
      console.error('Firebase Storage upload error:', error)
      throw error
    }
  }

  // Firebase Firestore for data storage
  async saveToFirestore(collection: string, data: any, docId?: string): Promise<string> {
    try {
      const url = docId 
        ? `https://firestore.googleapis.com/v1/projects/${this.projectId}/databases/(default)/documents/${collection}/${docId}`
        : `https://firestore.googleapis.com/v1/projects/${this.projectId}/databases/(default)/documents/${collection}?documentId=${docId}`

      const response = await fetch(url, {
        method: docId ? 'PATCH' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          fields: this.objectToFields(data)
        })
      })

      if (!response.ok) {
        throw new Error('Failed to save to Firestore')
      }

      const result = await response.json()
      return result.name?.split('/').pop() || docId || Date.now().toString()
    } catch (error) {
      console.error('Firestore save error:', error)
      throw error
    }
  }

  // Get data from Firestore
  async getFromFirestore(collection: string, docId: string): Promise<any> {
    try {
      const response = await fetch(
        `https://firestore.googleapis.com/v1/projects/${this.projectId}/databases/(default)/documents/${collection}/${docId}`,
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`
          }
        }
      )

      if (!response.ok) {
        throw new Error('Failed to get from Firestore')
      }

      const data = await response.json()
      return this.fieldsToObject(data.fields)
    } catch (error) {
      console.error('Firestore get error:', error)
      throw error
    }
  }

  // Query Firestore collection
  async queryFirestore(collection: string, limit: number = 10): Promise<any[]> {
    try {
      const response = await fetch(
        `https://firestore.googleapis.com/v1/projects/${this.projectId}/databases/(default)/documents/${collection}?pageSize=${limit}`,
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`
          }
        }
      )

      if (!response.ok) {
        throw new Error('Failed to query Firestore')
      }

      const data = await response.json()
      return data.documents?.map((doc: any) => ({
        id: doc.name?.split('/').pop(),
        ...this.fieldsToObject(doc.fields)
      })) || []
    } catch (error) {
      console.error('Firestore query error:', error)
      throw error
    }
  }

  // Firebase Authentication (for user management)
  async signInWithGoogle(): Promise<any> {
    try {
      // This would require Firebase SDK for proper auth
      // For now, return a mock implementation
      return {
        user: {
          uid: 'mock-user-id',
          email: 'user@example.com',
          displayName: 'Anime User'
        },
        token: 'mock-token'
      }
    } catch (error) {
      console.error('Firebase Auth error:', error)
      throw error
    }
  }

  // Firebase Realtime Database (for real-time features)
  async saveToRealtime(path: string, data: any): Promise<void> {
    try {
      const response = await fetch(
        `https://${this.projectId}-default-rtdb.firebaseio.com/${path}.json`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        }
      )

      if (!response.ok) {
        throw new Error('Failed to save to Realtime Database')
      }
    } catch (error) {
      console.error('Realtime Database save error:', error)
      throw error
    }
  }

  // Helper method to convert JavaScript object to Firestore fields
  private objectToFields(obj: any): any {
    const fields: any = {}
    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'string') {
        fields[key] = { stringValue: value }
      } else if (typeof value === 'number') {
        fields[key] = { integerValue: value.toString() }
      } else if (typeof value === 'boolean') {
        fields[key] = { booleanValue: value }
      } else if (Array.isArray(value)) {
        fields[key] = { arrayValue: { values: value.map(item => this.objectToFields(item)) } }
      } else if (typeof value === 'object' && value !== null) {
        fields[key] = { mapValue: { fields: this.objectToFields(value) } }
      } else {
        fields[key] = { nullValue: null }
      }
    }
    return fields
  }

  // Helper method to convert Firestore fields to JavaScript object
  private fieldsToObject(fields: any): any {
    const obj: any = {}
    for (const [key, value] of Object.entries(fields)) {
      const field = value as any
      if ('stringValue' in field) {
        obj[key] = field.stringValue
      } else if ('integerValue' in field) {
        obj[key] = parseInt(field.integerValue)
      } else if ('booleanValue' in field) {
        obj[key] = field.booleanValue
      } else if ('arrayValue' in field) {
        obj[key] = field.arrayValue.values?.map(item => this.fieldsToObject(item)) || []
      } else if ('mapValue' in field) {
        obj[key] = this.fieldsToObject(field.mapValue.fields || {})
      } else {
        obj[key] = null
      }
    }
    return obj
  }
}

export const firebaseService = new FirebaseService()
