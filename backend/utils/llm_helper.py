import os
from groq import Groq
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# User provided key - typically should be valid env var
# Ensure GROQ_API_KEY is set in CI/CD secrets

def get_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY not found in environment variables.")
        return None
    return Groq(api_key=api_key)

def summarize_context_shift(topic, word, old_context, new_context):
    """
    Uses Llama 3.1 to generate a 'common man' explanation of the shift.
    """
    client = get_client()
    
    prompt = f"""
    You are an expert linguist explaining semantic drift to a non-technical person.
    
    Topic: {topic}
    Word: "{word}"
    
    Old Context (How it was used before):
    {old_context}
    
    New Context (How it is used now):
    {new_context}
    
    Task: Explain how the meaning or usage of the word "{word}" has changed in the context of "{topic}".
    
    Constraint:
    - WRITE EXACTLY ONE PARAGRAPH.
    - DO NOT use bullet points or lists.
    - Start directly with the explanation.
    - Keep it under 60 words.
    - Be conversational but accurate.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_completion_tokens=150,
            top_p=1,
            stream=False,
            stop=None
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq generation failed: {e}")
        return None

def generate_context_bullets(raw_snippets, word, is_old=True):
    """
    Converts raw text snippets into clean, readable bullet points.
    """
    if not raw_snippets:
        return []
    
    client = get_client()
    if not client:
        return raw_snippets  # Fallback to raw if no API
    
    timeframe = "previously" if is_old else "now"
    snippets_text = "\n".join([f"- {s}" for s in raw_snippets])
    
    prompt = f"""
    You are analyzing how the word "{word}" is being used in social media discussions.
    
    Raw text examples from {timeframe}:
    {snippets_text}
    
    Task: Based on these examples, write 1-2 SHORT, CLEAR bullet points (max 15 words each) that explain what "{word}" referred to {timeframe}.
    
    Rules:
    - Each bullet should be a complete, readable sentence
    - Focus on the MEANING or CONTEXT, not the raw text
    - Be concise and clear
    - Return ONLY the bullet points, nothing else
    - Start each line with a dash (-)
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_completion_tokens=100,
            top_p=1,
            stream=False,
            stop=None
        )
        result = completion.choices[0].message.content.strip()
        # Parse the bullet points
        bullets = [line.strip().lstrip('-').strip() for line in result.split('\n') if line.strip().startswith('-')]
        return bullets if bullets else raw_snippets
    except Exception as e:
        logger.error(f"Failed to generate context bullets: {e}")
        return raw_snippets  # Fallback to raw

def explain_graph_trend(trend_data):
    """
    Summarizes the drift trend from the time-series data.
    trend_data: List of dicts with 'date', 'avg_semantic_drift', 'avg_concept_accuracy'
    """
    client = get_client()
    
    # Simplify data for prompt to save tokens
    summary_str = "\n".join([f"{d['date']}: SemDrift={d['avg_semantic_drift']}, ConAcc={d['avg_concept_accuracy']}" for d in trend_data])
    
    prompt = f"""
    Analyze the following drift trend data for an intent monitoring dashboard.
    
    Metric Definitions:
    - Semantic Drift: Higher is BAD (more meaning change).
    - Concept Accuracy: Lower is BAD (model failing).
    
    Data:
    {summary_str}
    
    Task: Write a 1-2 sentence summary of the overall trend for the dashboard header.
    - Is the system stable or degrading?
    - Only mention specific dates if there was a sudden spike.
    - Tone: Professional, analytical.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_completion_tokens=100,
            top_p=1,
            stream=False,
            stop=None
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq generation failed: {e}")
        return None
