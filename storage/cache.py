import logging

logger = logging.getLogger(__name__)

class TranscriptCache:
    """
    In-memory cache for YouTube transcripts.
    Keyed by video_id to avoid redundant API calls.
    """
    def __init__(self):
        self._cache = {}

    def get_transcript(self, video_id: str) -> list[dict] | None:
        """Retrieves cached transcript segments for a video ID."""
        return self._cache.get(video_id)

    def set_transcript(self, video_id: str, segments: list[dict]):
        """Caches transcript segments for a video ID."""
        self._cache[video_id] = segments
        logger.info(f"Transcript cached for video: {video_id}")

    def clear(self):
        """Clears the entire cache."""
        self._cache.clear()
        logger.info("Transcript cache cleared.")

# Global instance of the transcript cache
transcript_cache = TranscriptCache()
