"""Google Gemini client for Drupal Aggregator."""
import os
from typing import Optional, Dict, Any


def generate_summary(
    prompt: str,
    model: str = "gemini-1.5-pro",
    temperature: float = 0.2,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate summary using Google Gemini API.

    Returns:
        dict with 'text', 'tokens', and 'model' keys
    """
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("Google Generative AI package not installed. Install with: pip install google-generativeai>=0.7")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set in environment")

    genai.configure(api_key=api_key)

    try:
        model_obj = genai.GenerativeModel(
            model_name=model,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": kwargs.get("max_tokens", 4000),
            }
        )

        system_prompt = "You are a technical writer specializing in Drupal documentation."
        full_prompt = f"{system_prompt}\n\n{prompt}"

        response = model_obj.generate_content(full_prompt)

        # Estimate tokens (Gemini doesn't always provide exact counts)
        tokens = kwargs.get("estimated_tokens", len(prompt.split()) * 1.3)

        return {
            "text": response.text,
            "tokens": int(tokens),
            "model": model,
            "provider": "gemini"
        }
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {str(e)}")
