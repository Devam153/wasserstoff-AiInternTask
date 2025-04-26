from fastapi import APIRouter, Depends, HTTPException, Request, Header
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import uuid
import json

from backend.core.game_logic import validate_guess, get_game_session, create_game_session
from backend.core.ai_client import get_ai_response
from backend.core.moderation import check_content
from backend.db.models import increment_guess_count, get_guess_count

router = APIRouter()

class GuessRequest(BaseModel):
    guess: str
    session_id: Optional[str] = None

class GameResponse(BaseModel):
    success: bool
    message: str
    session_id: str
    current_word: str
    score: int
    game_over: bool
    guess_history: List[str]
    global_count: int = 0

@router.post("/start")
async def start_game(request: Request):
    """Start a new game session with 'Rock' as the seed word."""
    session_id = str(uuid.uuid4())
    session = await create_game_session(session_id, "Rock")
    
    return {
        "success": True,
        "message": "Game started! Try to guess what beats 'Rock'.",
        "session_id": session_id,
        "current_word": "Rock",
        "score": 0,
        "game_over": False,
        "guess_history": []
    }

@router.post("/guess")
async def make_guess(
    guess_request: GuessRequest, 
    request: Request,
    x_persona: Optional[str] = Header("serious")
):
    """Submit a guess for what beats the current word."""
    # Get session
    if not guess_request.session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")
    
    session = await get_game_session(guess_request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    # Check if game is already over
    if session.get("game_over", False):
        return {
            "success": False,
            "message": "Game is already over!",
            "session_id": guess_request.session_id,
            "current_word": session["current_word"],
            "score": session["score"],
            "game_over": True,
            "guess_history": session["history"]
        }
    
    # Validate the input (moderation check)
    guess = guess_request.guess.strip()
    is_safe, reason = check_content(guess)
    if not is_safe:
        return {
            "success": False,
            "message": f"Your guess was flagged: {reason}",
            "session_id": guess_request.session_id,
            "current_word": session["current_word"],
            "score": session["score"],
            "game_over": False,
            "guess_history": session["history"]
        }
    
    # Process the guess
    current_word = session["current_word"]
    
    # Check if this guess is a duplicate in the session
    if guess.lower() in [item.lower() for item in session["history"]]:
        # Update session as game over
        await validate_guess(
            guess_request.session_id, 
            guess, 
            current_word, 
            is_valid=False, 
            game_over=True, 
            reason="duplicate"
        )
        
        return {
            "success": False,
            "message": f"Game Over! You already guessed '{guess}'.",
            "session_id": guess_request.session_id,
            "current_word": current_word,
            "score": session["score"],
            "game_over": True,
            "guess_history": session["history"]
        }
    
    # Get AI validation
    redis = request.app.state.redis
    cache_key = f"validation:{current_word.lower()}:{guess.lower()}"
    
    # Check cache first
    cached_result = await redis.get(cache_key)
    if cached_result:
        is_valid = json.loads(cached_result)["is_valid"]
    else:
        # If not in cache, ask the AI
        is_valid = await get_ai_response(guess, current_word, persona=x_persona)
        
        # Cache the result
        await redis.set(
            cache_key, 
            json.dumps({"is_valid": is_valid}),
            expire=3600  # Cache for 1 hour
        )
    
    # Update game state based on validation
    result = await validate_guess(
        guess_request.session_id, 
        guess, 
        current_word, 
        is_valid=is_valid,
        game_over=False
    )
    
    # Update global counter for this guess if valid
    global_count = 0
    if is_valid:
        global_count = await increment_guess_count(guess)
    else:
        global_count = await get_guess_count(guess)
    
    # Generate response based on persona
    if is_valid:
        if x_persona == "cheery":
            message = f"✨ Woohoo! '{guess}' totally beats '{current_word}'! Your guess has been made {global_count} times before. Keep going! 🎉"
        else:  # serious persona
            message = f"✅ Correct. '{guess}' beats '{current_word}'. This answer has been submitted {global_count} times globally."
    else:
        if x_persona == "cheery":
            message = f"Aww, sorry! It seems '{guess}' doesn't beat '{current_word}'. Try something else! 🤔"
        else:  # serious persona
            message = f"Incorrect. '{guess}' does not beat '{current_word}'. Please try again."
    
    # Get updated session
    updated_session = await get_game_session(guess_request.session_id)
    
    return {
        "success": is_valid,
        "message": message,
        "session_id": guess_request.session_id,
        "current_word": updated_session["current_word"] if is_valid else current_word,
        "score": updated_session["score"],
        "game_over": updated_session.get("game_over", False),
        "guess_history": updated_session["history"],
        "global_count": global_count
    }

@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get the guess history for a specific game session."""
    session = await get_game_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    return {
        "session_id": session_id,
        "current_word": session["current_word"],
        "score": session["score"],
        "game_over": session.get("game_over", False),
        "guess_history": session["history"]
    }

@router.get("/stats/{guess}")
async def get_guess_statistics(guess: str):
    """Get global statistics for a specific guess."""
    count = await get_guess_count(guess)
    return {
        "guess": guess,
        "global_count": count
    }

@router.delete("/reset/{session_id}")
async def reset_game(session_id: str):
    """Reset a game session (for testing purposes)."""
    await create_game_session(session_id, "Rock")
    return {"message": f"Game session {session_id} has been reset."}