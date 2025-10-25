"""LM Studio client for Drupal Aggregator."""
import os
from typing import Optional, Dict, Any
import httpx


def generate_summary(
    prompt: str,
    model: str = "qwen2.5:7b-instruct",
    temperature: float = 0.2,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate summary using LM Studio local API (OpenAI compatible).

    Returns:
        dict with 'text', 'tokens', and 'model' keys
    """
    base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234")

    try:
        response = httpx.post(
            f"{base_url}/v1/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a technical writer specializing in Drupal documentation."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": kwargs.get("max_tokens", 4000)
            },
            timeout=120.0
        )
        response.raise_for_status()

        data = response.json()
        text = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)

        # Estimate if not provided
        if tokens == 0:
            tokens = len(prompt.split()) + len(text.split())

        return {
            "text": text,
            "tokens": tokens,
            "model": model,
            "provider": "lmstudio"
        }
    except httpx.HTTPError as e:
        raise RuntimeError(f"LM Studio API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"LM Studio error: {str(e)}")
