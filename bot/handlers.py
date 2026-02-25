import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.utils import extract_youtube_id
from services.transcript_service import fetch_transcript_segments
from services.chunking_service import chunk_transcript
from services.summarizer import generate_summary
from services.qa_engine import answer_question

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I'm your YouTube Summarizer Bot. "
        "Send me a YouTube link to summarize it, or ask me questions about the last video we processed!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detect YouTube URL for summarization OR handle questions for Q&A."""
    text = update.message.text
    if not text:
        return

    video_id = extract_youtube_id(text)
    
    # 1. Handle YouTube URL (Summarization)
    if video_id:
        status_message = await update.message.reply_text(
            f"Valid YouTube link detected! (ID: {video_id})\nFetching transcript..."
        )
        
        try:
            segments = fetch_transcript_segments(video_id)
            chunks = chunk_transcript(segments)
            
            # Store chunks in user session for Q&A
            context.user_data['last_transcript_chunks'] = chunks
            context.user_data['last_video_id'] = video_id
            
            if len(chunks) > 1:
                await status_message.edit_text(
                    f"Transcript fetched! Splitting into {len(chunks)} parts for processing...\n"
                    "Generating comprehensive summary..."
                )
            else:
                await status_message.edit_text("Transcript fetched! Generating summary...")
            
            summary = generate_summary(chunks)
            await status_message.edit_text(summary)
            await update.message.reply_text("You can now ask me follow-up questions about this video!")
            
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            await status_message.edit_text(f"Sorry, I encountered an error during summarization: {str(e)}")
    
    # 2. Handle non-URL text (Q&A)
    else:
        chunks = context.user_data.get('last_transcript_chunks')
        if not chunks:
            await update.message.reply_text(
                "I don't have a transcript in memory yet. "
                "Please send me a YouTube link first, and then you can ask questions about it!"
            )
            return

        status_message = await update.message.reply_text("Thinking...")
        try:
            answer = answer_question(text, chunks)
            await status_message.edit_text(answer)
        except Exception as e:
            logger.error(f"Q&A error: {str(e)}")
            await status_message.edit_text(f"Sorry, I couldn't answer that: {str(e)}")



