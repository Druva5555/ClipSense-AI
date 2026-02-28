import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Ensure OPENCLAW_BASE_URL is set in your .env file.
# Defaults to Ollama's local endpoint if missing.
client = OpenAI(
    base_url=os.getenv("OPENCLAW_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.getenv("OPENCLAW_API_KEY", "openclaw-local")
)

# Use the model defined in the environment or fallback to llama3.2
MODEL_NAME = os.getenv("OPENCLAW_MODEL", "llama3.2")

def load_prompt_template(file_path: str) -> str:
    """Loads the prompt template from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

from storage.cache import transcript_cache

def generate_summary(transcript: str | list[str], language: str = "English", prompt_file: str = "prompts/summary_prompt.txt", video_id: str = None) -> str:
    """
    Generates a structured output from a transcript using an LLM based on a provided prompt file.
    Handles both single strings and lists of chunks. Includes caching if video_id is provided.
    """
    cache_key = None
    if video_id:
        cache_key = f"{video_id}_{language}_{prompt_file}"
        cached_summary = transcript_cache.get_summary(cache_key)
        if cached_summary:
            logger.info(f"Cache hit for summary: {cache_key}")
            return cached_summary

    if isinstance(transcript, list):
        if len(transcript) == 1:
            result = _generate_single_summary(transcript[0], language, prompt_file)
        else:
            result = _summarize_multiple_chunks(transcript, language, prompt_file)
    else:
        result = _generate_single_summary(transcript, language, prompt_file)
        
    if cache_key and result:
        transcript_cache.set_summary(cache_key, result)
        
    return result

def _generate_single_summary(text: str, language: str, prompt_file: str) -> str:
    """Internal helper for single text summarization."""
    try:
        prompt_template = load_prompt_template(prompt_file)
        full_prompt = prompt_template.format(transcript=text, language=language)

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": f"You are a professional YouTube video analyst. Respond in {language}."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Error in _generate_single_summary: {str(e)}")
        if "rate_limit_exceeded" in str(e).lower():
            raise Exception("The bot is currently experiencing high demand (Rate Limit). Please try again in a few minutes.")
        raise e

def _summarize_multiple_chunks(chunks: list[str], language: str, prompt_file: str) -> str:
    """
    Summarizes multiple chunks by first summarizing each, then combining them based on the target prompt.
    """
    logger.info(f"Processing {len(chunks)} chunks in {language} for {prompt_file}...")
    intermediate_summaries = []
    
    for i, chunk in enumerate(chunks):
        try:
            # Concise summary for each chunk to build context
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": f"Summarize this part of a YouTube transcript concisely in {language}, capturing key points and timestamps."},
                    {"role": "user", "content": f"Transcript part {i+1}:\n\n{chunk}"}
                ],
                temperature=0.5,
            )
            intermediate_summaries.append(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error summarizing chunk {i}: {str(e)}")
            continue

    # Final reduction step uses the target prompt
    combined_summaries = "\n\n".join(intermediate_summaries)
    return _generate_single_summary(combined_summaries, language, prompt_file)


