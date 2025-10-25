from __future__ import annotations

import importlib
from pathlib import Path
from textwrap import dedent
from typing import List, Sequence

import yaml
from loguru import logger

from utils.dedupe import ItemDict
from utils.providers.base import ProviderSettings
from utils.providers.common import fallback_summary


class ProviderLoadError(RuntimeError):
    pass


def _load_config(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not data or "providers" not in data:
        raise ProviderLoadError("providers.yaml is missing required keys")
    return data


def _build_prompt(items: Sequence[ItemDict], tz: str, days: int) -> str:
    intro = dedent(
        f"""
        You are compiling the official Drupal weekly digest.
        Timeframe: past {days} days ({tz}).
        Highlight AI/automation, Drupal core releases, Admin UI/Canvas, and new contrib modules.
        Use concise Markdown with sections: Core & Security, Modules & Releases, AI & Automation, Canvas/Admin UI, Additional Notes.
        Each bullet must cite the URL as a Markdown link. If no qualifying updates exist for a section, write "No significant updates" for that section.
        Facts only, no hype. Include release versions and statuses when available.
        """
    ).strip()
    lines = [intro, "\nCollected items:"]
    for item in items:
        lines.append(
            dedent(
                f"""
                - title: {item.get('title')}
                  url: {item.get('url')}
                  summary: {item.get('summary')}
                  published: {item.get('published')}
                  category: {item.get('category')}
                """
            ).strip()
        )
    if not items:
        lines.append("- None")
    return "\n".join(lines)


def _instantiate_provider(module_name: str, settings: ProviderSettings):
    module = importlib.import_module(f"utils.providers.{module_name}")
    if hasattr(module, "create"):
        return module.create(settings)
    client_cls = next((getattr(module, attr) for attr in dir(module) if attr.endswith("Client")), None)
    if client_cls:
        return client_cls(settings)
    raise ProviderLoadError(f"Provider module {module_name} is missing a factory")


def summarize(
    items: List[ItemDict],
    provider_name: str,
    *,
    model_override: str | None,
    providers_config_path: Path,
    timezone: str,
    days: int,
    dry_run: bool = False,
) -> str:
    config = _load_config(providers_config_path)
    providers = config.get("providers", {})
    if provider_name not in providers:
        raise ProviderLoadError(f"Unknown provider '{provider_name}'")

    provider_cfg = providers[provider_name]
    settings = ProviderSettings(
        name=provider_name,
        model=model_override or provider_cfg.get("model"),
        temperature=float(provider_cfg.get("temperature", 0.2)),
        max_output_tokens=provider_cfg.get("max_output_tokens"),
    )

    prompt = _build_prompt(items, timezone, days)

    if dry_run:
        logger.warning("[ai_summarizer] running in dry-run mode; using fallback summary")
        return _fallback(items)

    try:
        provider = _instantiate_provider(provider_cfg["client"], settings)
        summary = provider.summarize(prompt, max_tokens=settings.max_output_tokens)
        if "[" not in summary:
            logger.warning("[ai_summarizer] summary missing references; appending fallback references")
            summary += "\n\n" + _fallback(items)
        return summary
    except Exception as exc:  # pragma: no cover - safety net
        logger.error("[ai_summarizer] provider failed: {}", exc)
        return _fallback(items)


def _fallback(items: Sequence[ItemDict]) -> str:
    titles = [item.get("title", "") for item in items[:10]]
    base = fallback_summary(titles)
    references = "\n".join(f"- [{item.get('title')}]({item.get('url')})" for item in items[:10])
    if not references:
        references = "- No significant core updates this week."
    return base + "\n\nReferences:\n" + references
