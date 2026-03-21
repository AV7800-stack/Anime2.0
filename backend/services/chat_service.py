import openai
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
import asyncio

load_dotenv()

class ChatService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def chat_with_ai(self, message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Chat with AI assistant specialized for anime generation
        """
        try:
            if conversation_history is None:
                conversation_history = []
            
            # System prompt for anime assistant
            system_prompt = """You are an AI assistant specialized in anime generation and creative storytelling. 

Your role is to:
1. Help users create amazing anime content
2. Provide creative suggestions for anime stories, characters, and scenes
3. Assist with prompt engineering for better AI generation results
4. Be friendly, creative, and enthusiastic about anime
5. Understand anime tropes, styles, and genres

You have access to these generation capabilities:
- Story generation (anime narratives, plots, character development)
- Image generation (anime characters, scenes, art styles)
- Video generation (animated scenes, character animations)

Always respond in a helpful, creative, and engaging way. Use anime-related examples and references when appropriate. Be encouraging and help users refine their ideas."""

            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history (last 10 messages to avoid token limits)
            for msg in conversation_history[-10:]:
                messages.append(msg)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Generate response
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.8,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            ai_response = response.choices[0].message.content
            
            # Analyze if user wants to generate content
            generation_intent = self._analyze_generation_intent(message)
            
            return {
                "success": True,
                "response": ai_response,
                "generation_intent": generation_intent,
                "suggestions": self._get_suggestions(message, generation_intent),
                "timestamp": str(asyncio.get_event_loop().time())
            }
            
        except Exception as e:
            print(f"❌ Chat service error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "मुझे अभी बात नहीं कर सकता, कृपया थोड़ी देर बाद फिर कोशिश करें।"
            }
    
    def _analyze_generation_intent(self, message: str) -> Dict[str, Any]:
        """
        Analyze user message to understand what they want to generate
        """
        message_lower = message.lower()
        
        intent = {
            "wants_story": False,
            "wants_image": False,
            "wants_video": False,
            "needs_help": False,
            "has_idea": False
        }
        
        # Story indicators
        story_keywords = ["कहानी", "story", "कथा", "narrative", "plot", "कहानी लिखो", "write story"]
        intent["wants_story"] = any(keyword in message_lower for keyword in story_keywords)
        
        # Image indicators
        image_keywords = ["चित्र", "image", "character", "फोटो", "photo", "drawing", "डिजाइन", "design"]
        intent["wants_image"] = any(keyword in message_lower for keyword in image_keywords)
        
        # Video indicators
        video_keywords = ["वीडियो", "video", "animation", "एनिमेशन", "scene", "animated"]
        intent["wants_video"] = any(keyword in message_lower for keyword in video_keywords)
        
        # Help indicators
        help_keywords = ["मदद", "help", "कैसे", "how", "सुझाव", "suggestion", "आइडिया", "idea"]
        intent["needs_help"] = any(keyword in message_lower for keyword in help_keywords)
        
        # Has idea indicators
        idea_keywords = ["मेरे पास आइडिया है", "i have an idea", "सोचा है", "मैं बनाना चाहता हूं"]
        intent["has_idea"] = any(keyword in message_lower for keyword in idea_keywords)
        
        return intent
    
    def _get_suggestions(self, message: str, intent: Dict[str, Any]) -> List[str]:
        """
        Get contextual suggestions based on user intent
        """
        suggestions = []
        
        if intent["wants_story"]:
            suggestions.extend([
                "क्या आप एक एनीमे कहानी बनाना चाहते हैं?",
                "मैं आपके लिए एक रोमांटिक एनीमे कहानी लिख सकता हूं",
                "एक्शन से भरपूर शोनेन कहानी चाहिए?"
            ])
        
        if intent["wants_image"]:
            suggestions.extend([
                "एक एनीमे कैरेक्टर बनाना चाहते हैं?",
                "मैं आपके लिए ब्लू हेयर वाला वॉरियर कैरेक्टर बना सकता हूं",
                "मैजिकल गर्ल कैरेक्टर चाहिए?"
            ])
        
        if intent["wants_video"]:
            suggestions.extend([
                "एनिमेटेड सीन बनाना चाहते हैं?",
                "फाइटिंग सीन एनिमेट करना है?",
                "रोमांटिक सीन बनाना चाहिए?"
            ])
        
        if intent["needs_help"]:
            suggestions.extend([
                "मैं आपको आइडिया दे सकता हूं",
                "कौन सा एनीमे जेनर पसंद है?",
                "क्या आप Studio Ghibli स्टाइल पसंद करते हैं?"
            ])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    async def get_conversation_starters(self) -> List[str]:
        """
        Get conversation starters for new users
        """
        return [
            "मैं एक एनीमे कहानी बनाना चाहता हूं",
            "मुझे एक एनीमे कैरेक्टर बनाने में मदद चाहिए",
            "क्या आप मेरे लिए एक एनीे वीडियो बना सकते हैं?",
            "मुझे एक अच्छा आइडिया चाहिए",
            "मैं कैसे बेहतर प्रॉम्प्ट लिख सकता हूं?"
        ]
    
    async def get_anime_suggestions(self, genre: str = None) -> Dict[str, List[str]]:
        """
        Get anime suggestions based on genre
        """
        suggestions = {
            "shonen": [
                "ड्रैगन बॉल जैसी एक्शन कहानी",
                "निन्जा ट्रेनिंग सीन",
                "पावर-अप ट्रांसफॉर्मेशन"
            ],
            "shojo": [
                "रोमांटिक हाई स्कूल कहानी",
                "मैजिकल गर्ल ट्रांसफॉर्मेशन",
                "हार्टब्रेकिंग लव स्टोरी"
            ],
            "seinen": [
                "साइबरपंक थ्रिलर",
                "साइकोलॉजिकल ड्रामा",
                "पोस्ट-अपोकैलिप्टिक एडवेंचर"
            ],
            "studio_ghibli": [
                "व्हिस्परिंग विंड्स जैसी जादुई कहानी",
                "नेचर सीन विद स्पिरिट कैरेक्टर्स",
                "स्टीमपंक एडवेंचर"
            ]
        }
        
        if genre and genre.lower() in suggestions:
            return {genre: suggestions[genre.lower()]}
        
        return suggestions

# Global instance
chat_service = ChatService()
