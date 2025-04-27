
from better_profanity import profanity
import re
from typing import List, Set

# Initialize profanity filter with extra censored words if needed
profanity.load_censor_words()

# Additional disallowed words (can be expanded)
DISALLOWED_WORDS: Set[str] = {
    "slur", "explicit", "offensive"
}

# Regex patterns for content that should be flagged
DANGEROUS_PATTERNS = [
    r"(^|\s)kill(\s|$|ing|ed)",
    r"(^|\s)harm(\s|$|ing|ed)",
    r"(^|\s)hurt(\s|$|ing|ed)",
    r"(^|\s)injure(\s|$|ing|ed)",
]

def check_content(text: str) -> bool:
    """
    Check if content contains profanity or disallowed content
    Returns True if content should be blocked
    """
    if not text or not isinstance(text, str):
        return False
    
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Check for profanity
    if profanity.contains_profanity(text):
        return True
    
    # Check for disallowed words
    for word in DISALLOWED_WORDS:
        if word in text_lower.split():
            return True
    
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    
    return False