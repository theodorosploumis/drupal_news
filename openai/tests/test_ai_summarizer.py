from pathlib import Path

import yaml

from src import ai_summarizer


def test_summarize_dry_run(tmp_path):
    providers_path = tmp_path / "providers.yaml"
    providers_path.write_text(
        yaml.safe_dump(
            {
                "default_provider": "openai",
                "providers": {
                    "openai": {"client": "openai_client", "model": "gpt-4.1-mini"}
                },
            }
        ),
        encoding="utf-8",
    )
    items = [
        {
            "title": "New Drupal module",
            "url": "https://www.drupal.org/project/foo",
            "summary": "Adds foo integration",
            "published": "2025-10-17T09:00:00+03:00",
            "source": "https://www.drupal.org",
            "kind": "rss",
        }
    ]
    summary = ai_summarizer.summarize(
        items,
        "openai",
        model_override=None,
        providers_config_path=providers_path,
        timezone="Europe/Athens",
        days=7,
        dry_run=True,
    )
    assert "Automated fallback summary" in summary
    assert "https://www.drupal.org/project/foo" in summary
