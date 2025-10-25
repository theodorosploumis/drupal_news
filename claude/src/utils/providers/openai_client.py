"""OpenAI client for Drupal Aggregator."""
import os
from typing import Optional, Dict, Any


def generate_summary(
    prompt: str,
    model: str = "gpt-4.1-mini",
    temperature: float = 0.2,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate summary using OpenAI API.

    Returns:
        dict with 'text', 'tokens', and 'model' keys
    """
    try:
        import openai
    except ImportError:
        raise ImportError("OpenAI package not installed. Install with: pip install openai>=1.45")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")

    client = openai.OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a technical writer specializing in Drupal documentation."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=kwargs.get("max_tokens", 4000)
        )

        return {
            "text": response.choices[0].message.content,
            "tokens": response.usage.total_tokens,
            "model": model,
            "provider": "openai"
        }
    except Exception as e:
        raise RuntimeError(f"OpenAI API error: {str(e)}")
