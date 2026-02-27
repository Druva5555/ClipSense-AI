import re

SUPPORTED_LANGUAGES = {
    'telugu': 'Telugu',
    'english': 'English'
}

def detect_language(text: str) -> str:
    """
    Simple keyword-based language detection.
    Looks for patterns like "in Telugu", "explain in Hindi", etc.
    Defaults to 'English' if no match is found.
    """
    text_lower = text.lower()
    
    for key, name in SUPPORTED_LANGUAGES.items():
        # Look for "in [language]" or just "[language]" in the request
        if re.search(rf"\b(in|to|into)\s+{key}\b", text_lower) or re.search(rf"\b{key}\b", text_lower):
            return name
            
    return "English"
