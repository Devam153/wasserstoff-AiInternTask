
// Game state variables
let sessionId = null;
let currentWord = null;
let score = 0;

// DOM elements
const seedWordInput = document.getElementById('seed-word');
const startGameButton = document.getElementById('start-game');
const guessInput = document.getElementById('guess-input');
const submitGuessButton = document.getElementById('submit-guess');
const currentWordDisplay = document.getElementById('current-word');
const resultMessage = document.getElementById('result-message');
const scoreElement = document.getElementById('score');
const globalCountElement = document.getElementById('global-count');
const guessesList = document.getElementById('guesses-list');
const personaSelector = document.getElementById('persona');
const gameOverModal = document.getElementById('game-over-modal');
const gameOverMessage = document.getElementById('game-over-message');
const finalScoreElement = document.getElementById('final-score');
const playAgainButton = document.getElementById('play-again');

// Event listeners
startGameButton.addEventListener('click', startNewGame);
submitGuessButton.addEventListener('click', submitGuess);
playAgainButton.addEventListener('click', () => {
    gameOverModal.style.display = 'none';
    startNewGame();
});

// Enter key event listeners
guessInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        submitGuess();
    }
});

seedWordInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        startNewGame();
    }
});

// Functions
async function startNewGame() {
    const seedWord = seedWordInput.value.trim() || 'rock';
    
    try {
        const response = await fetch('/api/new-game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ seed_word: seedWord }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        
        const data = await response.json();
        sessionId = data.session_id;
        currentWord = data.current_word;
        score = 0;
        
        // Update UI
        currentWordDisplay.textContent = currentWord;
        scoreElement.textContent = '0';
        globalCountElement.textContent = '0';
        resultMessage.classList.add('hidden');
        
        // Update guesses list
        updateGuessesList([currentWord]);
        
        // Enable input fields
        guessInput.disabled = false;
        submitGuessButton.disabled = false;
        guessInput.value = '';
        guessInput.focus();
        
    } catch (error) {
        console.error('Error starting new game:', error);
        showMessage(`Error starting game: ${error.message}`, false);
    }
}

async function submitGuess() {
    if (!sessionId) {
        showMessage('Please start a new game first', false);
        return;
    }
    
    const guess = guessInput.value.trim();
    if (!guess) {
        showMessage('Please enter a guess', false);
        return;
    }
    
    try {
        const response = await fetch('/api/guess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'persona': personaSelector.value,
            },
            body: JSON.stringify({
                guess: guess,
                session_id: sessionId,
            }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update UI based on response
        if (data.valid) {
            // Success - update the game state
            currentWord = data.current_word;
            score = data.score;
            
            currentWordDisplay.textContent = currentWord;
            currentWordDisplay.classList.add('pulse');
            setTimeout(() => currentWordDisplay.classList.remove('pulse'), 500);
            
            scoreElement.textContent = score;
            globalCountElement.textContent = data.global_count;
            
            showMessage(data.message, true);
            updateGuessesList(data.previous_guesses);
            
            // Play success animation
            triggerConfetti();
            
        } else {
            // Failure or game over
            if (data.message.includes('Game Over')) {
                // Game over - show modal
                showGameOver(data.message, score);
            } else {
                // Just a wrong guess
                currentWordDisplay.classList.add('shake');
                setTimeout(() => currentWordDisplay.classList.remove('shake'), 500);
                showMessage(data.message, false);
            }
        }
        
        // Clear input for next guess
        guessInput.value = '';
        guessInput.focus();
        
    } catch (error) {
        console.error('Error submitting guess:', error);
        showMessage(`Error: ${error.message}`, false);
    }
}

function updateGuessesList(guesses) {
    guessesList.innerHTML = '';
    
    // Add the guesses in reverse order (most recent first)
    const recentGuesses = [...guesses].reverse();
    
    recentGuesses.forEach(guess => {
        const li = document.createElement('li');
        li.textContent = guess;
        guessesList.appendChild(li);
    });
}

function showMessage(message, isSuccess) {
    resultMessage.textContent = message;
    resultMessage.classList.remove('hidden', 'success', 'error');
    resultMessage.classList.add(isSuccess ? 'success' : 'error');
}

function showGameOver(message, finalScore) {
    gameOverMessage.textContent = message;
    finalScoreElement.textContent = finalScore;
    gameOverModal.style.display = 'flex';
}

function triggerConfetti() {
    confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 }
    });
}
