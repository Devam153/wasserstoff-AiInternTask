import motor.motor_asyncio
import os
from typing import Dict, Any, List, Optional

# Get database connection string from environment
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongodb:27017/guessgame")

# Connection instance
client = None
db = None

async def init_db():
    """Initialize the database connection."""
    global client, db
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
        db = client.guessgame
        
        # Create indexes
        await db.guess_counts.create_index("guess", unique=True)
        print("MongoDB initialized successfully")
        return True
    except Exception as e:
        print(f"MongoDB initialization error: {str(e)}")
        return False

async def increment_guess_count(guess: str) -> int:
    """Increment the global count for a specific guess."""
    try:
        result = await db.guess_counts.find_one_and_update(
            {"guess": guess.lower()},
            {"$inc": {"count": 1}},
            upsert=True,
            return_document=True
        )
        return result["count"]
    except Exception as e:
        print(f"Error incrementing guess count: {str(e)}")
        return 0

async def get_guess_count(guess: str) -> int:
    """Get the global count for a specific guess."""
    try:
        result = await db.guess_counts.find_one({"guess": guess.lower()})
        return result["count"] if result else 0
    except Exception as e:
        print(f"Error getting guess count: {str(e)}")
        return 0

async def save_game_session(session_id: str, data: Dict[str, Any]):
    """Save game session data."""
    try:
        await db.game_sessions.update_one(
            {"session_id": session_id},
            {"$set": data},
            upsert=True
        )
    except Exception as e:
        print(f"Error saving game session: {str(e)}")

async def get_game_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve game session data."""
    try:
        session = await db.game_sessions.find_one({"session_id": session_id})
        return session
    except Exception as e:
        print(f"Error retrieving game session: {str(e)}")
        return None