
from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import time
from typing import Optional

from backend.api import game_routes
from backend.core.cache import init_redis_pool
from backend.db.models import init_db

app = FastAPI(title="What Beats Rock - AI Game")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you should specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Get client IP
    client_ip = request.client.host
    
    # Simple in-memory rate limiting (in production, use Redis for this)
    # Allow 10 requests per minute per IP
    current_time = int(time.time())
    request_key = f"{client_ip}:{current_time // 60}"
    
    if hasattr(app.state, "rate_limits"):
        rate_limits = app.state.rate_limits
    else:
        rate_limits = {}
        app.state.rate_limits = rate_limits
    
    if request_key in rate_limits:
        rate_limits[request_key] += 1
        if rate_limits[request_key] > 100:  # Allow 100 requests per minute
            return HTTPException(status_code=429, detail="Too many requests")
    else:
        rate_limits[request_key] = 1
    
    response = await call_next(request)
    return response

# Mount API routes
app.include_router(game_routes.router)

# Mount static files for frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

@app.on_event("startup")
async def startup_db_client():
    await init_db()
    app.state.redis = await init_redis_pool()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
