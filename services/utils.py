import re

def extract_youtube_id(url: str) -> str | None:
    """
    Extracts the YouTube Video ID from various URL formats.
    Returns the ID if valid, else None.
    """
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",  # v=ID or /ID
        r"youtu\.be\/([0-9A-Za-z_-]{11})",  # youtu.be/ID
        r"youtube\.com\/shorts\/([0-9A-Za-z_-]{11})",  # shorts/ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
            
    return None

def is_valid_youtube_url(url: str) -> bool:
    """Checks if a string contains a valid YouTube URL."""
    return extract_youtube_id(url) is not None
