
import os
import google.generativeai as genai
from typing import Dict, Any
import json

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY", "")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

SERIOUS_PROMPT = """
You are a judge for a game called "What Beats What". 
Given a guess (X) and a word (Y), determine if X beats Y based on logical relationships, physics, common sense, or general knowledge.
Respond with a JSON object with these fields:
- valid: a boolean indicating if X beats Y (true or false)
- explanation: a brief explanation of your reasoning (max 15 words)

Examples:
- Paper beats Rock: {"valid": true, "explanation": "Paper covers rock"}
- Scissors beats Paper: {"valid": true, "explanation": "Scissors cut paper"}
- Rock beats Scissors: {"valid": true, "explanation": "Rock crushes scissors"}
- Flame beats Paper: {"valid": true, "explanation": "Fire burns paper"}

Think logically about physical properties, common knowledge relationships, or commonly accepted hierarchies. Be consistent.
Respond ONLY with a JSON object, nothing else.
"""

CHEERY_PROMPT = """
You are an ENTHUSIASTIC and FUN judge for a game called "What Beats What"!!! 😄🎮
Given a guess (X) and a word (Y), decide if X beats Y using logic, physics, pop culture, or just good fun! 
Be CREATIVE but fair!

Respond with a JSON object:
- valid: a boolean showing if X beats Y (true or false)
- explanation: a FUN, ENTHUSIASTIC explanation (max 15 words) with emojis!

Examples:
- Paper beats Rock: {"valid": true, "explanation": "Paper WRAPS that rock up tight! 📃✨"}
- Scissors beats Paper: {"valid": true, "explanation": "SNIP SNIP! Paper gets cut to pieces! ✂️💯"}
- Water beats Fire: {"valid": true, "explanation": "SPLASH! Fire gets extinguished! 💧🔥"}

Be CREATIVE, ENERGETIC, and ready to HAVE FUN! Use EMOJIS and keep it EXCITING!
Respond ONLY with a JSON object, nothing else.
"""

async def get_ai_response(guess: str, word: str, persona: str = "serious") -> Dict[str, Any]:
    """Get response from Gemini AI"""
    try:
        prompt = SERIOUS_PROMPT if persona.lower() == "serious" else CHEERY_PROMPT
        
        # Construct the prompt for Gemini
        content = f"{prompt}\n\nGuess (X): {guess}\nWord (Y): {word}"
        
        response = model.generate_content(content)
        
        # Parse the response
        try:
            # Extract JSON from response
            response_text = response.text
            result = json.loads(response_text)
            
            # Validate response structure
            if not isinstance(result, dict) or "valid" not in result or "explanation" not in result:
                return {"valid": False, "explanation": "AI response format error"}
                
            return result
        except json.JSONDecodeError:
            # Fallback parsing if JSON extraction fails
            response_text = response.text.lower()
            valid = "true" in response_text and "valid" in response_text
            explanation = "Based on AI judgment"
            return {"valid": valid, "explanation": explanation}
            
    except Exception as e:
        print(f"Error in AI response: {str(e)}")
        return {"valid": False, "explanation": "Error connecting to AI service"}