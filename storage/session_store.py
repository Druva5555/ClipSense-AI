import logging

logger = logging.getLogger(__name__)

class SessionStore:
    """
    In-memory session store for user transcript contexts.
    Each user has their own session keyed by user_id.
    """
    def __init__(self):
        self._sessions = {}

    def set_session(self, user_id: int, video_id: str, chunks: list[str]):
        """Stores the transcript chunks for a user session."""
        self._sessions[user_id] = {
            'video_id': video_id,
            'chunks': chunks
        }
        logger.info(f"Session stored for user {user_id} (video: {video_id})")

    def get_session(self, user_id: int) -> dict | None:
        """Retrieves the current session for a user."""
        return self._sessions.get(user_id)

    def clear_session(self, user_id: int):
        """Clears the session for a user."""
        if user_id in self._sessions:
            del self._sessions[user_id]
            logger.info(f"Session cleared for user {user_id}")

# Global instance of the session store
session_store = SessionStore()
