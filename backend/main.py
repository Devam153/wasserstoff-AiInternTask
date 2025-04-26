import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import os
from dotenv import load_dotenv
from typing import Optional

from backend.api.routes import router as api_router
from backend.core.cache import init_redis_pool
from backend.db.models import init_db

# Load environment variables
load_dotenv()

app = FastAPI(title="What Beats Rock - Game API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Implement a simple rate limiter
    # In a real application, this would use Redis for distributed rate limiting
    if not hasattr(app, "rate_limits"):
        app.rate_limits = {}
    
    if client_ip in app.rate_limits:
        last_request_time, count = app.rate_limits[client_ip]
        # Reset counter if more than 60 seconds have passed
        if current_time - last_request_time > 60:
            app.rate_limits[client_ip] = (current_time, 1)
        # Rate limit: 100 requests per minute
        elif count >= 100:
            return JSONResponse(
                status_code=429,
                content={"message": "Rate limit exceeded. Try again later."}
            )
        else:
            app.rate_limits[client_ip] = (last_request_time, count + 1)
    else:
        app.rate_limits[client_ip] = (current_time, 1)
    
    response = await call_next(request)
    return response

# Include API routes
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    # Initialize Redis connection pool
    app.state.redis = await init_redis_pool()
    
    # Initialize database
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    # Close Redis connection
    if hasattr(app.state, "redis"):
        await app.state.redis.close()

@app.get("/")
async def root():
    return {"message": "Welcome to What Beats Rock Game API. Go to /docs for API documentation."}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)