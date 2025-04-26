from better_profanity import profanity
from typing import Tuple
import re

# Initialize profanity filter
profanity.load_censor_words()

# Add additional disallowed content patterns
DISALLOWED_PATTERNS = [
    r'(^|\s)hack(\s|$|ing)',  # Hacking-related content
    r'(^|\s)(admin|password)(\s|$)',  # Security-sensitive terms
    r'<script>',  # Basic XSS prevention
    r'function\(\)',  # JavaScript code
    r'SELECT.*FROM',  # SQL injection attempt
]

def check_content(text: str) -> Tuple[bool, str]:
    """
    Check if content contains disallowed text.
    
    Args:
        text: The text to check
        
    Returns:
        Tuple of (is_safe, reason)
    """
    # Check for profanity
    if profanity.contains_profanity(text):
        return False, "Contains inappropriate language"
    
    # Check for other disallowed patterns
    for pattern in DISALLOWED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, "Contains disallowed content"
    
    # Check for empty or too short input
    if not text or len(text.strip()) < 2:
        return False, "Input is too short"
    
    # Check for too long input
    if len(text) > 50:
        return False, "Input is too long (max 50 characters)"
    
    return True, ""