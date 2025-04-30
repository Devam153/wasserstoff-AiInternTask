
from fastapi import APIRouter, HTTPException, Depends, Header, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from backend.core.game_logic import GameSession, validate_beats
from backend.core.ai_client import get_ai_response
from backend.core.moderation import check_content
from backend.db.models import update_global_counter, get_global_counter, create_game_session, get_game_session

router = APIRouter(prefix="/api", tags=["game"])

class GuessRequest(BaseModel):
    guess: str
    session_id: str

class GuessResponse(BaseModel):
    valid: bool
    message: str
    current_word: str
    score: int
    previous_guesses: List[str]
    global_count: int

@router.post("/guess")
async def make_guess(
    guess_request: GuessRequest,
    persona: Optional[str] = Header("serious")
):
    guess = guess_request.guess.strip().lower()
    session_id = guess_request.session_id
    
    # Check for profanity
    if check_content(guess):
        raise HTTPException(status_code=400, detail="Inappropriate content detected")
    
    # Get game session
    game_session = await get_game_session(session_id)
    
    if not game_session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    # Get current word (the last guess or the seed)
    current_word = game_session["current_word"]
    
    # Check if the guess beats the current word
    result = await validate_beats(guess, current_word, persona)
    
    if not result["valid"]:
        message = f"❌ Sorry, \"{guess}\" doesn't beat \"{current_word}\"."
        return {
            "valid": False,
            "message": message,
            "current_word": current_word,
            "score": game_session["score"],
            "previous_guesses": game_session["guesses"][-5:] if "guesses" in game_session else [],
            "global_count": 0
        }
    
    # Check if the guess is already in the linked list
    if guess in game_session["guesses"]:
        return {
            "valid": False,
            "message": f"🎮 Game Over! \"{guess}\" was already guessed.",
            "current_word": current_word,
            "score": game_session["score"],
            "previous_guesses": game_session["guesses"][-5:],
            "global_count": await get_global_counter(guess)
        }
    
    # Update global counter
    global_count = await update_global_counter(guess)
    
    # Update game session
    game_session["guesses"].append(guess)
    game_session["current_word"] = guess
    game_session["score"] += 1
    
    await create_game_session(session_id, game_session)
    
    message = f"✅ Nice! \"{guess}\" beats \"{current_word}\". {guess} has been guessed {global_count} times before."
    
    return {
        "valid": True,
        "message": message,
        "current_word": guess,
        "score": game_session["score"],
        "previous_guesses": game_session["guesses"][-5:],
        "global_count": global_count
    }

@router.post("/new-game")
async def new_game(seed_word: str = "rock"):
    seed_word = seed_word.strip().lower()
    
    # Check for profanity in seed word
    if check_content(seed_word):
        raise HTTPException(status_code=400, detail="Inappropriate content detected in seed word")
    
    # Create a new game session
    session_id = await create_game_session(None, {
        "current_word": seed_word,
        "guesses": [seed_word],
        "score": 0
    })
    
    return {
        "session_id": session_id,
        "current_word": seed_word,
        "message": f"Game started with seed word: {seed_word}",
        "previous_guesses": [seed_word],
        "score": 0
    }

@router.get("/history/{session_id}")
async def get_history(session_id: str):
    game_session = await get_game_session(session_id)
    
    if not game_session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    return {
        "current_word": game_session["current_word"],
        "guesses": game_session["guesses"],
        "score": game_session["score"]
    }
