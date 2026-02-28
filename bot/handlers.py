import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.utils import extract_youtube_id
from services.transcript_service import fetch_transcript_segments
from services.chunking_service import chunk_transcript
from services.summarizer import generate_summary
from services.qa_engine import answer_question
from services.language_service import detect_language
from storage.session_store import session_store

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"👋 Hi {user.mention_html()}! I'm your YouTube Summarizer Bot. "
        "\n\nHere is what I can do:"
        "\n🎥 <b>Summarize</b>: Send me a YouTube link (or use /summary <url>)."
        "\n❓ <b>Ask</b>: Ask me questions about the video (or use /ask <question>)."
        "\n🤿 <b>Deep Dive</b>: Get a detailed breakdown of the video (use /deepdive)."
        "\n🎯 <b>Action Points</b>: Extract a to-do list from the video (use /actionpoints)."
        "\n🌐 <b>Language</b>: Use /language <lang> to set your preferred language."
    )

async def _process_analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt_file: str, action_name: str, emoji: str):
    """Generic handler for /deepdive and /actionpoints commands."""
    user_id = update.effective_user.id
    session = session_store.get_session(user_id)
    
    if not session or not session.get('chunks'):
        await update.message.reply_text(
            "👋 I don't have a video in memory yet!\n"
            "Please send me a YouTube link first, and then I can run this command."
        )
        return

    chunks = session['chunks']
    video_id = session.get('video_id')
    current_language = session.get('language', 'English')
    
    status_message = await update.message.reply_text(f"{emoji} Generating {action_name} in {current_language}... This might take a moment.")
    
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        result = generate_summary(chunks, language=current_language, prompt_file=prompt_file, video_id=video_id)
        await status_message.edit_text(result)
    except Exception as e:
        error_text = str(e)
        logger.error(f"{action_name} error: {error_text}")
        await status_message.edit_text(f"❌ {error_text}")

async def command_deepdive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /deepdive command."""
    await _process_analysis_command(update, context, "prompts/deepdive_prompt.txt", "Deep Dive", "🤿")

async def command_actionpoints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /actionpoints command."""
    await _process_analysis_command(update, context, "prompts/actionpoints_prompt.txt", "Action Points", "🎯")

async def command_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /summary command."""
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /summary <youtube_url>")
        return
    
    # Re-use the existing text handling logic by simulating a text message
    update.message.text = context.args[0]
    await handle_message(update, context)

async def command_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /ask command."""
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /ask <your question>")
        return
    
    # Re-use the existing text handling logic
    update.message.text = " ".join(context.args)
    await handle_message(update, context)

async def command_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /language command."""
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /language <English|Telugu>")
        return
    
    new_language = context.args[0].capitalize()
    user_id = update.effective_user.id
    
    if new_language not in ["English", "Telugu"]:
        await update.message.reply_text("❌ Currently, I only support English and Telugu.")
        return

    session = session_store.get_session(user_id)
    if session:
        session_store.update_language(user_id, new_language)
        await update.message.reply_text(f"🌐 Language updated to {new_language} for this session.")
    else:
        # Create an empty session just to store the language preference
        session_store.set_session(user_id, "", [], language=new_language)
        await update.message.reply_text(f"🌐 Language preference set to {new_language}. Send me a video!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detect YouTube URL for summarization OR handle questions for Q&A with multilingual support."""
    text = update.message.text
    if not text:
        return

    video_id = extract_youtube_id(text)
    user_id = update.effective_user.id
    
    # 1. Handle YouTube URL (Summarization)
    if video_id:
        target_language = detect_language(text)
        
        status_message = await update.message.reply_text(
            f"🔍 Valid YouTube link detected!\n"
            f"⏳ Fetching transcript and preparing {target_language} summary..."
        )
        
        try:
            # Show typing indicator for long operations
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            segments = fetch_transcript_segments(video_id)
            chunks = chunk_transcript(segments)
            
            # Store chunks and detected language in session
            session_store.set_session(user_id, video_id, chunks, language=target_language)
            
            if len(chunks) > 1:
                await status_message.edit_text(
                    f"✅ Transcript fetched! This is a long video, processing {len(chunks)} parts...\n"
                    f"✍️ Generating {target_language} summary. This might take a moment..."
                )
            else:
                await status_message.edit_text(f"✅ Transcript fetched!\n✍️ Generating {target_language} summary...")
            
            # Keep typing indicator alive for long summaries
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            summary = generate_summary(chunks, language=target_language, video_id=video_id)
            
            await status_message.edit_text(summary)
            await update.message.reply_text(f"✨ You can now ask me follow-up questions in any language (Default: {target_language})!")
            
        except Exception as e:
            error_text = str(e)
            logger.error(f"Summarization error: {error_text}")
            await status_message.edit_text(f"❌ {error_text}")
    
    # 2. Handle non-URL text (Q&A)
    else:
        session = session_store.get_session(user_id)
        
        if not session or not session.get('chunks'):
            await update.message.reply_text(
                "👋 I don't have a video in memory yet!\n"
                "Please send me a YouTube link first, and then I can help you with questions."
            )
            return

        chunks = session['chunks']
        # Check if user explicitly requested a different language in this question
        current_language = session.get('language', 'English')
        requested_language = detect_language(text)
        
        # If the user explicitly mentioned a language in the question, update session
        if "in" in text.lower() and requested_language != "English":
             current_language = requested_language
             session_store.update_language(user_id, current_language)

        status_message = await update.message.reply_text(f"🤔 Thinking ({current_language})...")
        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            video_id = session.get('video_id')
            answer = answer_question(text, chunks, language=current_language, video_id=video_id)
            
            await status_message.edit_text(answer)
        except Exception as e:
            error_text = str(e)
            logger.error(f"Q&A error: {error_text}")
            await status_message.edit_text(f"⚠️ {error_text}")
