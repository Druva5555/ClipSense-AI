import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Note: Using OpenAI as a default provider for the "OpenClaw" request.
# Ensure OPENAI_API_KEY is set in your .env file.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_prompt_template(file_path: str) -> str:
    """Loads the prompt template from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_summary(transcript: str | list[str], language: str = "English") -> str:
    """
    Generates a structured summary from a transcript using an LLM.
    Handles both single strings and lists of chunks.
    """
    if isinstance(transcript, list):
        if len(transcript) == 1:
            return _generate_single_summary(transcript[0], language)
        else:
            return _summarize_multiple_chunks(transcript, language)
    return _generate_single_summary(transcript, language)

def _generate_single_summary(text: str, language: str) -> str:
    """Internal helper for single text summarization."""
    try:
        prompt_template = load_prompt_template("prompts/summary_prompt.txt")
        full_prompt = prompt_template.format(transcript=text, language=language)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a professional YouTube video summarizer. Respond in {language}."},
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

def _summarize_multiple_chunks(chunks: list[str], language: str) -> str:
    """
    Summarizes multiple chunks by first summarizing each, then combining them.
    """
    logger.info(f"Summarizing {len(chunks)} chunks in {language}...")
    intermediate_summaries = []
    
    for i, chunk in enumerate(chunks):
        try:
            # Concise summary for each chunk
            response = client.chat.completions.create(
                model="gpt-4o",
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

    # Final reduction step
    combined_summaries = "\n\n".join(intermediate_summaries)
    return _generate_single_summary(combined_summaries, language)


