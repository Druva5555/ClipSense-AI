import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.utils import extract_youtube_id
from services.transcript_service import fetch_transcript_segments
from services.chunking_service import chunk_transcript
from services.summarizer import generate_summary

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I'm your YouTube Summarizer Bot. "
        "Send me a YouTube link, and I'll summarize it for you!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detect YouTube URL, fetch transcript (with chunking), and generate summary."""
    text = update.message.text
    if not text:
        return

    video_id = extract_youtube_id(text)
    
    if video_id:
        status_message = await update.message.reply_text(
            f"Valid YouTube link detected! (ID: {video_id})\nFetching transcript..."
        )
        
        try:
            # 1. Fetch segments
            segments = fetch_transcript_segments(video_id)
            
            # 2. Chunk transcript
            chunks = chunk_transcript(segments)
            
            # 3. Inform user about processing
            if len(chunks) > 1:
                await status_message.edit_text(
                    f"Transcript fetched! Splitting into {len(chunks)} parts for processing...\n"
                    "Generating comprehensive summary..."
                )
            else:
                await status_message.edit_text("Transcript fetched! Generating summary...")
            
            # 4. Generate summary
            summary = generate_summary(chunks)
            
            # 5. Send final summary
            await status_message.edit_text(summary)
            
        except Exception as e:
            logger.error(f"Handler error: {str(e)}")
            await status_message.edit_text(f"Sorry, I encountered an error: {str(e)}")
    else:
        await update.message.reply_text(
            "Oops! That doesn't look like a valid YouTube link. "
            "Please send a link like https://www.youtube.com/watch?v=... or https://youtu.be/..."
        )


