# ClipSense AI - Telegram YouTube Summarizer

A Telegram bot that acts as a personal AI research assistant for YouTube videos.

## Features
- ** Generate Summaries**: Extracts the title, key points, important timestamps, and a core takeaway.
- ** Contextual Q&A**: Ask follow-up questions about the video. The bot is strictly grounded in the transcript and prevents hallucinations, explicitly returning "This topic is not covered in the video" when out of bounds.
- ** Multilingual Support**: Full support for summarizing and answering questions in English and Telugu (as the chosen Indian language).
- ** Additional Commands**: Includes `/deepdive` for extensive breakdowns and `/actionpoints` for extracting actionable to-do lists.

## 1. Setup Instructions (OpenClaw Local Integration)

This project is built to run entirely locally using the OpenClaw abstraction (implemented locally via Ollama).

1. **Install Prerequisites**: Ensure you have Python 3.10+ installed.
2. **Setup Local LLM**: Install [Ollama](https://ollama.com/) to process AI requests locally.
   - Run: `ollama run llama3.2` (This acts as the local OpenClaw engine).
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**: Create a `.env` file in the root directory:
   ```env
   BOT_TOKEN=your_telegram_bot_token_from_botfather
   OPENCLAW_BASE_URL=http://localhost:11434/v1
   OPENCLAW_MODEL=llama3.2
   OPENCLAW_API_KEY=openclaw-local
   ```
5. **Start the Bot**:
   ```bash
   python main.py
   ```

## 2. Architecture Explanation

The application follows a modular service architecture:
- **`bot/handlers.py`**: Manages the Telegram interaction layer, routing commands, showing typing indicators, and managing the active UX.
- **`services/transcript_service.py`**: Interacts with the public `youtube-transcript-api` to pull robust captions, falling back to auto-generated transcripts if manual ones are unavailable.
- **`services/chunking_service.py`**: Handles excessively long videos by breaking the transcript down into 8,000-character chunks while preserving `[MM:SS]` timestamps for accurate temporal context.
- **`services/language_service.py`**: Detects if a user is speaking in Telugu or English to dynamically route prompt translations.
- **`storage/session_store.py`**: Manages state per user (`user_id`). This allows the bot to handle multiple users simultaneously, remembering which video and which language preference each specific user is currently querying.
- **`storage/cache.py`**: A robust, in-memory dual-layer cache. It stores both the raw YouTube transcripts (to avoid API blocks on repeated links) and the final AI responses mapped to hashed query keys (skipping the LLM generation entirely on repeat identical queries).

## 3. Design Trade-offs

1. **In-Memory Caching vs. Database**: 
   - *Trade-off*: I opted to use in-memory dictionaries for transcript and context caching (`storage/cache.py`) instead of a heavy database like Redis or PostgreSQL.
   - *Reasoning*: For a Telegram bot prototype, memory access is exponentially faster and removes the complexity of managing a separate database container, fulfilling the cost optimization & speed requirements perfectly. The cache is wiped on restart, preventing stale data buildup.
2. **Context Stuffing vs. RAG (Retrieval-Augmented Generation)**:
   - *Trade-off*: The bot currently concatenates chunked transcript text and stuffs it into the LLM context window rather than using vector embeddings.
   - *Reasoning*: Modern local models (like `llama3.2`) have substantial context windows. Stuffing preserves the exact temporal narrative of a video, which is critical for YouTube summarization, whereas vector DBs often fragment the timeline.
3. **Local Compute (OpenClaw) vs. Cloud Providers**:
   - *Trade-off*: Running inference locally via Ollama trades generation speed for zero API costs and total data privacy. 

## Evaluation Criteria Addressed
- **End-to-End Functionality**: Fully handles the standard flow (Link -> Summary -> Q&A).
- **Summary Quality**: Strictly uses the required structured formats.
- **Q&A Accuracy**: Instructed via prompts to never hallucinate.
- **Multi-language**: Fully dynamic prompts supporting Telugu outputs and question parsing.
- **Error Handling**: Custom wrappers to catch disabled subtitle exceptions gracefully.
