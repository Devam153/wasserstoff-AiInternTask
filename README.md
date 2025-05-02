# wasserstoff-AiInternTask

# What Beats Rock - AI-Powered Guessing Game

A Generative AI-powered game where players try to guess what "beats" a given word.

## How to Play

1. The game starts with a seed word (e.g., "Rock").
2. You need to guess something that "beats" the current word.
3. The AI will determine if your guess is valid.
4. If valid, your score increases, and the current word changes to your guess.
5. If you repeat a guess that's already in your history, the game ends.
6. Try to build the longest chain of valid guesses!

## Architectural Choices

### Backend Architecture

- **FastAPI**: Chosen for its high performance, async support, and built-in documentation.
- **Linked List Implementation**: Used to track the chain of valid guesses with O(1) append time.
- **Database Schema**: Simple PostgreSQL schema for storing global guess counts.
- **Redis Caching**: Implemented to cache AI verdicts, reducing API calls and latency.

### Concurrency and Rate Limiting

- **Connection Pooling**: Used with PostgreSQL and Redis for efficient resource utilization.
- **Async I/O**: Leveraged FastAPI's async capabilities for handling concurrent requests.
- **Rate Limiting**: Middleware-based IP rate limiting to prevent abuse.

### AI Integration

- **Prompt Engineering**: Compact prompts to minimize token usage and cost.
- **Error Resilience**: Graceful fallback if AI service is unavailable.
- **Multiple Personas**: Support for different AI response styles.

### Caching Strategy

- **Redis TTL**: AI verdicts are cached with a 1-hour expiration to balance freshness and efficiency.
- **Input Normalization**: Inputs are normalized before caching to improve hit rates.

## Prompt Design

The AI prompts were designed to be:

1. **Concise**: Keeping token usage minimal ("Does X beat Y? Answer YES or NO only").
2. **Specific**: Clearly defining what "beat" means in this context.
3. **Persona-based**: Different system prompts for "serious" vs "cheery" host personalities.

## Deployment

This project includes:

- Docker and Docker Compose configuration for one-click deployment
- Streamlit frontend for cloud deployment on platforms like Render

## Future Improvements

- Implement user accounts for persistent scores
- Add difficulty levels with different AI strictness
- Create a multiplayer mode
- Optimize Redis cache eviction policies
- Add more advanced animations and visual feedback

---

© 2024 - Built as an internship task for Wasserstoff
