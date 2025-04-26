import os
import google.generativeai as genai
from typing import Tuple, Dict, Any, Optional
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

async def get_ai_response(guess: str, current_word: str, persona: str = "serious") -> bool:
    """
    Ask the AI whether guess beats current_word using Gemini.
    Returns True if guess beats current_word, False otherwise.
    """
    try:
        # Get the appropriate system prompt based on persona
        system_prompt = get_system_prompt(persona)
        
        # Create the model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create the prompt
        prompt = f"{system_prompt}\n\nDoes '{guess}' beat '{current_word}'? Answer YES or NO only."
        
        # Generate response
        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )
        
        # Extract the text and check for YES
        answer = response.text.strip().upper()
        return "YES" in answer
        
    except Exception as e:
        print(f"Error in Gemini AI response: {str(e)}")
        # Graceful degradation - flip a coin if AI fails
        import random
        return random.choice([True, False])

def get_system_prompt(persona: str) -> str:
    """Return the appropriate system prompt based on the selected persona."""
    if persona == "cheery":
        return """You are the enthusiastic host of a fun word game called 'What Beats What'! 
                Your job is to decide if one thing can beat another. Be creative but consistent! 
                Answer only YES or NO."""
    else:  # default to serious
        return """You are the logical judge of a word game. 
                Determine if the first item can defeat or overcome the second item. 
                Use common sense relationships. Answer only YES or NO."""