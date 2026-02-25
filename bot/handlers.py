import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.utils import extract_youtube_id

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I'm your YouTube Summarizer Bot. "
        "Send me a YouTube link, and I'll summarize it for you!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if the received message contains a valid YouTube URL."""
    text = update.message.text
    if not text:
        return

    video_id = extract_youtube_id(text)
    
    if video_id:
        await update.message.reply_text(
            f"Valid YouTube link detected! ID: {video_id}\n"
            "(Processing/Transcription coming soon...)"
        )
    else:
        await update.message.reply_text(
            "Oops! That doesn't look like a valid YouTube link. "
            "Please send a link like https://www.youtube.com/watch?v=... or https://youtu.be/..."
        )

