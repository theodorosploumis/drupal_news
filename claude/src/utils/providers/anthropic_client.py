"""Anthropic Claude client for Drupal Aggregator."""
import os
from typing import Optional, Dict, Any


def generate_summary(
    prompt: str,
    model: str = "claude-3-5-sonnet-20241022",
    temperature: float = 0.2,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate summary using Anthropic API.

    Returns:
        dict with 'text', 'tokens', and 'model' keys
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("Anthropic package not installed. Install with: pip install anthropic>=0.34")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")

    client = anthropic.Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=kwargs.get("max_tokens", 4000),
            temperature=temperature,
            system="You are a technical writer specializing in Drupal documentation.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return {
            "text": response.content[0].text,
            "tokens": response.usage.input_tokens + response.usage.output_tokens,
            "model": model,
            "provider": "anthropic"
        }
    except Exception as e:
        raise RuntimeError(f"Anthropic API error: {str(e)}")
