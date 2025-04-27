
import os
import uuid
import motor.motor_asyncio
from typing import Dict, Any, Optional, List

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = "what_beats_rock"

client = None
db = None

async def init_db():
    """Initialize database connection"""
    global client, db
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    # Ensure indexes
    await db.global_counters.create_index("word", unique=True)
    await db.game_sessions.create_index("session_id", unique=True)

async def create_game_session(session_id: Optional[str], data: Dict[str, Any]) -> str:
    """Create a new game session or update existing one"""
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Add session_id to data
    data["session_id"] = session_id
    
    # Upsert the game session
    await db.game_sessions.update_one(
        {"session_id": session_id},
        {"$set": data},
        upsert=True
    )
    
    return session_id

async def get_game_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get a game session by ID"""
    if not session_id:
        return None
    
    result = await db.game_sessions.find_one({"session_id": session_id})
    return result

async def update_global_counter(word: str) -> int:
    """Update global counter for a word and return new count"""
    result = await db.global_counters.find_one_and_update(
        {"word": word.lower()},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=True
    )
    
    return result.get("count", 1)

async def get_global_counter(word: str) -> int:
    """Get global counter for a word"""
    result = await db.global_counters.find_one({"word": word.lower()})
    return result.get("count", 0) if result else 0

async def reset_game_state():
    """Reset all game state - useful for testing"""
    await db.game_sessions.delete_many({})
    await db.global_counters.delete_many({})
