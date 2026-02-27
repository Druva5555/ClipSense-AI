import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _load_prompt_template(file_path: str) -> str:
    """Loads the prompt template from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def answer_question(question: str, chunks: list[str], language: str = "English") -> str:
    """
    Generates an answer to a user question based on transcript chunks.
    """
    try:
        # For now, we combine all chunks as context. 
        # In a more advanced version, we would use RAG/embeddings to find relevant chunks.
        context_text = "\n\n---\n\n".join(chunks)
        
        # Limit context to avoid token limit issues (rough estimate)
        if len(context_text) > 40000:
             # Take the first 40k chars as a fallback
            context_text = context_text[:40000] + "\n\n[Transcript truncated due to length...]"

        prompt_template = _load_prompt_template("prompts/qa_prompt.txt")
        full_prompt = prompt_template.format(context=context_text, question=question, language=language)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a strict Q&A assistant. You answer questions ONLY using the provided context. Respond in {language}. If the answer is not in the context, say 'This topic is not covered in the video.'"},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0, # Lower temperature for factual accuracy
        )


        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in answer_question: {str(e)}")
        if "rate_limit_exceeded" in str(e).lower():
             raise Exception("The bot is currently experiencing high demand (Rate Limit). Please try again in a few minutes.")
        raise Exception(f"Failed to generate answer: {str(e)}")
