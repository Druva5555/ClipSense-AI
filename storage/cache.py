import logging

logger = logging.getLogger(__name__)

class TranscriptCache:
    """
    In-memory cache for YouTube transcripts.
    Keyed by video_id to avoid redundant API calls.
    """
    def __init__(self):
        self._cache = {}
        self._summary_cache = {} # Keyed by f"{video_id}_{language}_{prompt_file}"

    def get_transcript(self, video_id: str) -> list[dict] | None:
        """Retrieves cached transcript segments for a video ID."""
        return self._cache.get(video_id)

    def set_transcript(self, video_id: str, segments: list[dict]):
        """Caches transcript segments for a video ID."""
        self._cache[video_id] = segments
        logger.info(f"Transcript cached for video: {video_id}")

    def get_summary(self, cache_key: str) -> str | None:
        """Retrieves a cached AI summary/analysis."""
        return self._summary_cache.get(cache_key)

    def set_summary(self, cache_key: str, summary: str):
        """Caches an AI summary/analysis string."""
        self._summary_cache[cache_key] = summary
        logger.info(f"Summary cached for key: {cache_key}")

    def clear(self):
        """Clears the entire cache."""
        self._cache.clear()
        self._summary_cache.clear()
        logger.info("Transcript and summary caches cleared.")

# Global instance of the transcript cache
transcript_cache = TranscriptCache()
