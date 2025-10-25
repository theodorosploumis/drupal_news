"""AI summarizer for Drupal Newsletter."""
import importlib
from typing import List, Dict, Any, Optional
from pathlib import Path
import time
from markdown_converter import items_to_text


SUMMARIZER_PROMPT_TEMPLATE = """
You are a technical writer for the Drupal community. Generate a summary of Drupal news and updates.

**Requirements:**
1. Focus on AI module and news on AI
2. Each fact MUST include a [source](URL) link
3. Use clear, factual language - no hype
4. If no major updates: include "No significant core updates this week"
5. Present RSS/new modules as a table with columns: URL, Name, Description
6. Organize by sections: Core Updates, Modules, AI/Automation, Canvas/Admin UI, Planet, D.O. Blog

**Timeframe:** Last {timeframe_days} days ({timezone})

**Items to summarize:**

{items_text}

Generate the summary in Markdown format with proper sections and source links.
"""


def load_prompt_template(prompt_file: str = None) -> str:
    """
    Load prompt template from markdown file or use default.

    Args:
        prompt_file: Path to prompt.md file (default: prompt.md in project root)

    Returns:
        Prompt template string with placeholders
    """
    if prompt_file is None:
        # Default to prompt.md in the project root
        prompt_file = Path(__file__).parent.parent / 'prompt.md'

    prompt_path = Path(prompt_file)

    if prompt_path.exists():
        try:
            return prompt_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not read {prompt_file}: {e}")
            print("Using default hardcoded prompt template")

    # Fall back to hardcoded default
    return SUMMARIZER_PROMPT_TEMPLATE


def get_provider_client(provider_name: str):
    """
    Dynamically load provider client module.

    Args:
        provider_name: Provider name (e.g., 'openai', 'anthropic')

    Returns:
        Provider client module
    """
    try:
        module = importlib.import_module(f"utils.providers.{provider_name}_client")
        return module
    except ImportError as e:
        raise ImportError(f"Provider '{provider_name}' not found: {e}")


def summarize(
    items: List[Dict[str, Any]],
    provider: str,
    model: str,
    temperature: float,
    timeframe_days: int,
    timezone: str,
    max_items: int = 200,
    chunk_size: int = 200
) -> Dict[str, Any]:
    """
    Generate AI summary of items.

    Args:
        items: List of news items
        provider: AI provider name
        model: Model name
        temperature: Temperature setting
        timeframe_days: Number of days covered
        timezone: Timezone name
        max_items: Maximum items to process
        chunk_size: Chunk size for large inputs

    Returns:
        Dictionary with 'text', 'tokens', 'model', 'provider', 'duration'
    """
    start_time = time.time()

    # Load provider client
    client = get_provider_client(provider)

    # Convert items to text
    items_text = items_to_text(items, max_items)

    # Load prompt template from file or use default
    template = load_prompt_template()

    # Generate prompt
    prompt = template.format(
        timeframe_days=timeframe_days,
        timezone=timezone,
        items_text=items_text
    )

    # Check if chunking needed
    if len(items) > chunk_size:
        # Chunked summarization
        summary_result = _summarize_chunked(
            client, items, prompt, model, temperature, chunk_size
        )
    else:
        # Single summarization
        try:
            summary_result = client.generate_summary(
                prompt=prompt,
                model=model,
                temperature=temperature
            )
        except Exception as e:
            raise RuntimeError(f"Summarization failed: {str(e)}")

    # Add duration
    duration = time.time() - start_time
    summary_result["duration"] = duration

    return summary_result


def _summarize_chunked(
    client,
    items: List[Dict[str, Any]],
    base_prompt: str,
    model: str,
    temperature: float,
    chunk_size: int
) -> Dict[str, Any]:
    """
    Summarize items in chunks for large datasets.

    Args:
        client: Provider client module
        items: List of items
        base_prompt: Base prompt template
        model: Model name
        temperature: Temperature
        chunk_size: Size of each chunk

    Returns:
        Combined summary result
    """
    summaries = []
    total_tokens = 0

    # Split into chunks
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        chunk_text = items_to_text(chunk)

        prompt = base_prompt.replace("{items_text}", chunk_text)

        try:
            result = client.generate_summary(
                prompt=prompt,
                model=model,
                temperature=temperature
            )

            summaries.append(result["text"])
            total_tokens += result.get("tokens", 0)

        except Exception as e:
            print(f"Warning: Chunk {i // chunk_size + 1} failed: {e}")

    # Combine summaries
    combined_text = "\n\n".join(summaries)

    return {
        "text": combined_text,
        "tokens": total_tokens,
        "model": model,
        "provider": client.__name__.split(".")[-1].replace("_client", ""),
        "chunked": True
    }


def summarize_with_fallback(
    items: List[Dict[str, Any]],
    providers_config: Dict[str, Any],
    default_provider: str,
    timeframe_days: int,
    timezone: str,
    fallback_order: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Summarize with automatic fallback to other providers.

    Args:
        items: List of news items
        providers_config: Providers configuration
        default_provider: Default provider to try first
        timeframe_days: Days covered
        timezone: Timezone name
        fallback_order: Optional custom fallback order

    Returns:
        Summary result with provider info
    """
    if fallback_order is None:
        fallback_order = ["openai", "anthropic", "ollama", "qwen", "openrouter"]

    # Try default provider first
    provider_list = [default_provider] + [p for p in fallback_order if p != default_provider]

    last_error = None

    for provider_name in provider_list:
        provider_config = providers_config.get("providers", {}).get(provider_name)

        if not provider_config:
            continue

        try:
            result = summarize(
                items=items,
                provider=provider_name,
                model=provider_config["model"],
                temperature=provider_config.get("temperature", 0.2),
                timeframe_days=timeframe_days,
                timezone=timezone
            )

            return result

        except Exception as e:
            last_error = e
            print(f"Provider {provider_name} failed: {e}")
            continue

    # All providers failed
    raise RuntimeError(f"All providers failed. Last error: {last_error}")


def generate_placeholder_summary(items: List[Dict[str, Any]], timeframe_days: int) -> str:
    """
    Generate placeholder summary for dry-run mode.

    Args:
        items: List of items
        timeframe_days: Days covered

    Returns:
        Placeholder markdown summary
    """
    return f"""# Drupal Newesleter Summary (Dry Run)

**Timeframe:** Last {timeframe_days} days

## Summary

This is a placeholder summary for dry-run mode.
Total items collected: {len(items)}

### Core Updates
No significant core updates this week.

### New Modules
{len([i for i in items if i.get('source_type') == 'rss'])} new modules found.

### AI and Automation
No major AI updates this week.

---
*This is a dry-run summary. Enable AI provider for actual summaries.*
"""
