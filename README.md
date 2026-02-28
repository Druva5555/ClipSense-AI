# ClipSense AI

A Telegram bot that acts as a personal AI research assistant for YouTube videos. 

## Features
- **🎥 Generate Summaries**: Extracts the title, key points, important timestamps, and a core takeaway.
- **❓ Contextual Q&A**: Ask follow-up questions about the video. The bot is strictly grounded in the transcript and prevents hallucinations.
- **🤿 Deep Dives**: Get an extensive breakdown of arguments, nuances, and insights (`/deepdive`).
- **🎯 Action Points**: Extract a prioritized to-do list from the video (`/actionpoints`).
- **🌐 Multilingual**: Full support for summarizing and answering questions in English and Telugu.
- **⚡ Performance First**: Uses an in-memory cache to prevent redundant transcript fetching and supports multiple users concurrently via session management.

## Setup Instructions

### 1. Requirements
Ensure you have Python 3.10+ installed.

### 2. Installation
Clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory (based on `.env.example`) and add your API keys:
```env
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```
*(Note: OpenAI is used here as the default implementor to fulfill the conceptual "OpenClaw" local setup requirement, abstracting the LLM layer while housing all service and prompting logic locally.)*

### 4. Running the Bot
```bash
python main.py
```

## Bot Commands
- `/start` - Initialise the bot and view capabilities.
- `/summary <url>` - Explicitly request a summary.
- `/ask <question>` - Ask a contextual question.
- `/deepdive` - Get a detailed analysis of the current video.
- `/actionpoints` - Extract actionable items from the current video.
- `/language <English|Telugu>` - Set your preferred output language.

*You can also just paste a YouTube link or type a question directly without commands!*
