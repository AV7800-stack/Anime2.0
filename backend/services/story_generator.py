import openai
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class StoryGenerator:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def generate_story(self, prompt: str, style: str = "anime", length: str = "medium") -> Dict[str, Any]:
        """
        Generate an anime story based on the given prompt.
        """
        try:
            # Determine story length
            length_instructions = {
                "short": "Write a short story (around 300-500 words)",
                "medium": "Write a medium-length story (around 800-1200 words)",
                "long": "Write a detailed story (around 1500-2000 words)"
            }
            
            length_prompt = length_instructions.get(length, length_instructions["medium"])
            
            # Create the system prompt
            system_prompt = f"""You are a professional anime story writer. Your task is to create engaging, creative anime stories that capture the essence of Japanese animation and storytelling.

Style requirements:
- Write in the {style} anime style
- Include vivid descriptions of characters and settings
- Create emotional depth and character development
- Use anime tropes and conventions appropriately
- Write in an engaging, narrative style

Structure:
- Start with an engaging opening
- Develop the plot with clear rising action
- Include character moments and dialogue
- Build to a satisfying climax
- Provide a thoughtful conclusion

{length_prompt}"""

            # Create the user prompt
            user_prompt = f"""Please write an anime story based on this prompt: {prompt}

Make sure to:
- Create compelling characters with distinct personalities
- Describe the setting in vivid detail
- Include dialogue that feels natural for anime characters
- Build emotional connections with the reader
- Use appropriate anime storytelling conventions"""

            # Generate the story
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000 if length == "long" else 1500 if length == "medium" else 800,
                temperature=0.8,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            story_content = response.choices[0].message.content
            
            # Extract a title from the story
            title = self._extract_title(prompt, story_content)
            
            return {
                "type": "story",
                "title": title,
                "content": story_content,
                "style": style,
                "length": length,
                "word_count": len(story_content.split()),
                "generated_at": str(openai.datetime.datetime.utcnow())
            }
            
        except Exception as e:
            print(f"❌ Error generating story: {e}")
            raise Exception(f"Failed to generate story: {str(e)}")
    
    def _extract_title(self, prompt: str, story_content: str) -> str:
        """Extract or generate a title based on the prompt and story"""
        # Simple title generation - in production, you could use AI for this
        prompt_words = prompt.split()[:5]
        base_title = " ".join(prompt_words).title()
        
        # Add anime-style suffixes
        anime_suffixes = ["Chronicles", "Tales", "Story", "Legend", "Saga", "Adventures"]
        
        # Simple logic to create a title
        if len(base_title) > 30:
            base_title = base_title[:30]
        
        # Return a formatted title
        return f"{base_title}: The Anime Story"
