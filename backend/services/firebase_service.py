import os
import requests
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

class FirebaseService:
    def __init__(self):
        self.api_key = os.getenv("FIREBASE_API_KEY")
        self.project_id = os.getenv("FIREBASE_PROJECT_ID")
        self.storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET")
        self.app_id = os.getenv("FIREBASE_APP_ID")
        
        if self.api_key and self.project_id:
            self.firebase_available = True
            print("✅ Firebase configured for storage and database")
        else:
            self.firebase_available = False
            print("⚠️ Firebase not configured")
    
    async def upload_to_storage(self, file_data: bytes, file_name: str, content_type: str = "image/jpeg") -> Optional[str]:
        """
        Upload file to Firebase Storage
        """
        if not self.firebase_available:
            return None
            
        try:
            # Upload to Firebase Storage via REST API
            url = f"https://firebasestorage.googleapis.com/v0/b/{self.storage_bucket}/o"
            
            headers = {
                "Content-Type": content_type,
                "Authorization": f"Bearer {self.api_key}"
            }
            
            params = {
                "name": file_name,
                "uploadType": "media"
            }
            
            response = requests.post(url, headers=headers, params=params, data=file_data)
            
            if response.status_code == 200:
                # Return download URL
                download_url = f"https://firebasestorage.googleapis.com/v0/b/{self.storage_bucket}/o/{file_name.replace('/', '%2F')}?alt=media"
                return download_url
            else:
                print(f"❌ Firebase Storage upload error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Firebase Storage error: {e}")
            return None
    
    async def save_to_firestore(self, collection: str, data: Dict[str, Any], doc_id: Optional[str] = None) -> Optional[str]:
        """
        Save data to Firestore
        """
        if not self.firebase_available:
            return None
            
        try:
            # Convert data to Firestore format
            firestore_data = self._convert_to_firestore_format(data)
            
            if doc_id:
                url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/{collection}/{doc_id}"
                method = "PATCH"
            else:
                url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/{collection}"
                method = "POST"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.request(method, url, headers=headers, json=firestore_data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                # Extract document ID from response
                if doc_id:
                    return doc_id
                else:
                    return result.get("name", "").split("/")[-1]
            else:
                print(f"❌ Firestore save error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Firestore error: {e}")
            return None
    
    async def get_from_firestore(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document from Firestore
        """
        if not self.firebase_available:
            return None
            
        try:
            url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/{collection}/{doc_id}"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return self._convert_from_firestore_format(data.get("fields", {}))
            else:
                print(f"❌ Firestore get error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Firestore get error: {e}")
            return None
    
    async def query_firestore(self, collection: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Query collection from Firestore
        """
        if not self.firebase_available:
            return []
            
        try:
            url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents/{collection}"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            params = {
                "pageSize": limit
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                documents = data.get("documents", [])
                
                results = []
                for doc in documents:
                    doc_id = doc.get("name", "").split("/")[-1]
                    doc_data = self._convert_from_firestore_format(doc.get("fields", {}))
                    doc_data["id"] = doc_id
                    results.append(doc_data)
                
                return results
            else:
                print(f"❌ Firestore query error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Firestore query error: {e}")
            return []
    
    async def save_to_realtime_database(self, path: str, data: Dict[str, Any]) -> bool:
        """
        Save data to Firebase Realtime Database
        """
        if not self.firebase_available:
            return False
            
        try:
            url = f"https://{self.project_id}-default-rtdb.firebaseio.com/{path}.json"
            
            response = requests.put(url, json=data)
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Realtime Database error: {e}")
            return False
    
    def _convert_to_firestore_format(self, data: Any) -> Dict[str, Any]:
        """
        Convert Python data to Firestore format
        """
        if isinstance(data, str):
            return {"stringValue": data}
        elif isinstance(data, int):
            return {"integerValue": str(data)}
        elif isinstance(data, float):
            return {"doubleValue": data}
        elif isinstance(data, bool):
            return {"booleanValue": data}
        elif isinstance(data, list):
            return {"arrayValue": {"values": [self._convert_to_firestore_format(item) for item in data]}}
        elif isinstance(data, dict):
            return {"mapValue": {"fields": {k: self._convert_to_firestore_format(v) for k, v in data.items()}}}
        else:
            return {"nullValue": None}
    
    def _convert_from_firestore_format(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Firestore format to Python data
        """
        result = {}
        for key, value in fields.items():
            if "stringValue" in value:
                result[key] = value["stringValue"]
            elif "integerValue" in value:
                result[key] = int(value["integerValue"])
            elif "doubleValue" in value:
                result[key] = float(value["doubleValue"])
            elif "booleanValue" in value:
                result[key] = value["booleanValue"]
            elif "arrayValue" in value:
                result[key] = [self._convert_from_firestore_format({"fields": item}) if isinstance(item, dict) else item 
                              for item in value["arrayValue"].get("values", [])]
            elif "mapValue" in value:
                result[key] = self._convert_from_firestore_format(value["mapValue"].get("fields", {}))
            else:
                result[key] = None
        return result

# Global instance
firebase_service = FirebaseService()
