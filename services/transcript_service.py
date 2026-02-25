import logging
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

logger = logging.getLogger(__name__)

def fetch_transcript(video_id: str) -> str:
    """
    Fetches the transcript for a given YouTube video ID.
    Returns the transcript as a single string.
    Raises Exception with a user-friendly message on failure.
    """
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        # Concatenate all text parts
        transcript_text = " ".join([item['text'] for item in transcript_list])
        return transcript_text
    except TranscriptsDisabled:
        raise Exception("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise Exception("No transcript found for this video.")
    except Exception as e:
        logger.error(f"Error fetching transcript for {video_id}: {str(e)}")
        raise Exception(f"Failed to fetch transcript: {str(e)}")
