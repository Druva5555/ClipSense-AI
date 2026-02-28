import os
import logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from bot.handlers import start, handle_message, command_summary, command_ask, command_language, command_deepdive, command_actionpoints

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

from telegram.request import HTTPXRequest

def main():
    """Start the bot."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables. Please check your .env file.")
        return

    # Bypass SSL verification for strict corporate networks and increase timeouts
    request = HTTPXRequest(
        connection_pool_size=8, 
        httpx_kwargs={"verify": False},
        connect_timeout=30.0,
        read_timeout=30.0
    )
    
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(BOT_TOKEN).request(request).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("summary", command_summary))
    application.add_handler(CommandHandler("ask", command_ask))
    application.add_handler(CommandHandler("language", command_language))
    application.add_handler(CommandHandler("deepdive", command_deepdive))
    application.add_handler(CommandHandler("actionpoints", command_actionpoints))
    
    # Handle non-command messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot started. Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main()
