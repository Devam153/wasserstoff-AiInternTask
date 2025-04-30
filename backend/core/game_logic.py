
from typing import Dict, Any, List, Optional
import uuid
from fastapi import Request

from backend.core.ai_client import get_ai_response
from backend.core.cache import make_cache_key, get_cache, set_cache

class GameSession:
    def __init__(self, seed_word: str = "rock"):
        self.id = str(uuid.uuid4())
        self.current_word = seed_word.lower()
        self.guesses = [seed_word.lower()]  # The linked list is represented as a list in order
        self.score = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert game session to dictionary for storage"""
        return {
            "id": self.id,
            "current_word": self.current_word,
            "guesses": self.guesses,
            "score": self.score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameSession':
        """Create game session from dictionary"""
        session = cls(data.get("current_word", "rock"))
        session.id = data.get("id", str(uuid.uuid4()))
        session.guesses = data.get("guesses", [session.current_word])
        session.score = data.get("score", 0)
        return session
    
    def add_guess(self, guess: str) -> bool:
        """Add a guess to the linked list if it doesn't exist already"""
        guess = guess.lower()
        if guess in self.guesses:
            return False  # Game over, duplicate guess
        
        self.guesses.append(guess)
        self.current_word = guess
        self.score += 1
        return True

async def validate_beats(guess: str, current_word: str, persona: str = "serious") -> Dict[str, Any]:
    """Validate if the guess beats the current word using AI"""
    # Import here to avoid circular imports
    from backend.main import app
    
    # Check cache if Redis is available
    if hasattr(app.state, "redis"):
        redis_client = app.state.redis
        cache_key = make_cache_key(guess, current_word, persona)
        cached_result = await get_cache(redis_client, cache_key)
        
        if cached_result:
            return cached_result
    
    # If not in cache, get from AI
    result = await get_ai_response(guess, current_word, persona)
    
    # Store in cache if Redis is available
    if hasattr(app.state, "redis"):
        redis_client = app.state.redis
        await set_cache(redis_client, cache_key, result)
    
    return result