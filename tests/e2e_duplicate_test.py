
import sys
import os
import asyncio
import pytest
from httpx import AsyncClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.db.models import init_db, reset_game_state

@pytest.fixture
async def client():
    """Create a test client for FastAPI application"""
    await init_db()
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    await reset_game_state()

@pytest.mark.asyncio
async def test_duplicate_guess_game_over(client):
    """Test that duplicate guess causes game over"""
    # Start a new game
    response = await client.post("/api/new-game", json={"seed_word": "rock"})
    assert response.status_code == 200
    data = response.json()
    session_id = data["session_id"]
    
    # First guess - paper beats rock (should succeed)
    response = await client.post(
        "/api/guess", 
        json={"guess": "paper", "session_id": session_id},
        headers={"persona": "serious"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == True
    assert "paper" in data["message"].lower()
    assert data["score"] == 1
    
    # Second guess - scissors beats paper (should succeed)
    response = await client.post(
        "/api/guess", 
        json={"guess": "scissors", "session_id": session_id},
        headers={"persona": "serious"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == True
    assert "scissors" in data["message"].lower()
    assert data["score"] == 2
    
    # Try to guess paper again (should fail with game over)
    response = await client.post(
        "/api/guess", 
        json={"guess": "paper", "session_id": session_id},
        headers={"persona": "serious"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == False
    assert "game over" in data["message"].lower()
    
    print("✅ End-to-end duplicate guess game over test passed!")

if __name__ == "__main__":
    asyncio.run(pytest.main(["-xvs", __file__]))