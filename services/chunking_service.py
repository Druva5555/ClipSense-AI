import logging

logger = logging.getLogger(__name__)

def chunk_transcript(segments: list[dict], max_chars: int = 8000) -> list[str]:
    """
    Groups transcript segments into chunks of text, each limited by max_chars.
    Preserves context by including the start timestamp at the beginning of each chunk.
    """
    chunks = []
    current_chunk = []
    current_count = 0
    
    for segment in segments:
        text = segment['text']
        start_time = segment['start']
        
        # Format: [MM:SS] Text
        minutes = int(start_time // 60)
        seconds = int(start_time % 60)
        formatted_segment = f"[{minutes:02d}:{seconds:02d}] {text} "
        
        if current_count + len(formatted_segment) > max_chars and current_chunk:
            chunks.append("".join(current_chunk).strip())
            current_chunk = []
            current_count = 0
            
        current_chunk.append(formatted_segment)
        current_count += len(formatted_segment)
        
    if current_chunk:
        chunks.append("".join(current_chunk).strip())
        
    return chunks
