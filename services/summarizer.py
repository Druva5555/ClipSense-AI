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

def generate_summary(transcript: str) -> str:
    """
    Generates a structured summary from a transcript using an LLM.
    """
    try:
        prompt_template = load_prompt_template("prompts/summary_prompt.txt")
        full_prompt = prompt_template.format(transcript=transcript)

        response = client.chat.completions.create(
            model="gpt-4o", # Or "claude-3-opus-20240229" if using an OpenClaw-like wrapper
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes YouTube videos."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise Exception(f"Failed to generate summary: {str(e)}")
