from typing import Dict, List, Optional, Tuple, Any
import json
import uuid
from backend.db.models import save_game_session, get_game_session

class GameNode:
    """A node in our linked list representing a valid guess."""
    def __init__(self, value: str):
        self.value = value
        self.next = None

class GameLinkedList:
    """A linked list to store the sequence of valid guesses."""
    def __init__(self, seed: str = "Rock"):
        self.head = GameNode(seed)
        self.tail = self.head
    
    def append(self, value: str) -> None:
        """Add a new node at the end of the linked list."""
        new_node = GameNode(value)
        self.tail.next = new_node
        self.tail = new_node
    
    def contains(self, value: str) -> bool:
        """Check if the linked list contains a specific value."""
        current = self.head
        while current:
            if current.value.lower() == value.lower():
                return True
            current = current.next
        return False
    
    def to_list(self) -> List[str]:
        """Convert the linked list to a regular list."""
        result = []
        current = self.head
        while current:
            result.append(current.value)
            current = current.next
        return result

async def create_game_session(session_id: str, seed_word: str = "Rock") -> Dict:
    """Create a new game session with initial seed word."""
    game_list = GameLinkedList(seed_word)
    session = {
        "session_id": session_id,
        "current_word": seed_word,
        "score": 0,
        "history": [seed_word],
        "game_over": False,
        "valid_guesses": [seed_word]
    }
    # Save to MongoDB
    await save_game_session(session_id, session)
    return session

async def validate_guess(
    session_id: str, 
    guess: str, 
    current_word: str, 
    is_valid: bool, 
    game_over: bool = False,
    reason: str = ""
) -> Dict:
    """
    Validate a guess and update the game state.
    """
    session = await get_game_session(session_id)
    if not session:
        return None
    
    # Update game history
    if guess not in session["history"]:
        session["history"].append(guess)
    
    # Check if game should end
    if game_over:
        session["game_over"] = True
        await save_game_session(session_id, session)
        return session
    
    # If AI says guess is valid
    if is_valid:
        session["valid_guesses"].append(guess)
        session["score"] += 1
        session["current_word"] = guess
        
    # Save updated session
    await save_game_session(session_id, session)
    return session