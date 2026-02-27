import logging
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

logger = logging.getLogger(__name__)

def fetch_transcript_segments(video_id: str) -> list[dict]:
    """
    Fetches the transcript segments for a given YouTube video ID.
    Returns a list of dicts: [{'text': str, 'start': float, 'duration': float}, ...]
    """
    try:
        return YouTubeTranscriptApi.get_transcript(video_id)
    except TranscriptsDisabled:
        raise Exception("Transcripts are disabled for this video. I can only summarize videos with available transcripts.")
    except NoTranscriptFound:
        raise Exception("No transcript was found for this video. It might not have subtitles or the language isn't supported.")
    except Exception as e:
        logger.error(f"Error fetching transcript for {video_id}: {str(e)}")
        if "VideoUnavailable" in str(e):
             raise Exception("This video is unavailable. It might be private or deleted.")
        raise Exception("I couldn't fetch the transcript for this video. Please check the link and try again.")

def fetch_transcript(video_id: str) -> str:
    """
    Fetches the transcript for a given YouTube video ID as a single string.
    """
    segments = fetch_transcript_segments(video_id)
    return " ".join([item['text'] for item in segments])

