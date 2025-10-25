# Drupal Weekly News Aggregator

This project compiles the previous week's Drupal highlights from official sources, summarizes them via pluggable AI providers, and emits Markdown, JSON, and email artifacts for human review.

## Features
- Fetches curated RSS feeds and canonical Drupal pages for the past seven days (Europe/Athens timezone).
- Deduplicates and validates items before generating structured outputs.
- Summaries produced by provider-specific adapters (OpenAI, Anthropic, Gemini, Ollama, LM Studio, Qwen, Grok, DeepSeek, OpenRouter) and exported as Markdown + PDF.
- Persistent caching with SQLite to avoid duplicate downloads.
- Structured logs, metrics, validation reports, and email-ready content saved per run under `runs/YYYY-MM-DD/`.
- Scheduler wrapper using APScheduler for easy automation.
- Cleanup utilities rotate old runs, logs, and cache entries.

## Quick Start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env .env.local  # customise secrets
python3 -m src.index --provider openai --email no
```

Use `python3 -m src.scheduler --help` for recurring runs. Tests live under `tests/` and can be executed with `pytest`.

To explore generated reports in the browser, install requirements and run:

```bash
python -m flask --app web_viewer run --debug
```

Then visit `http://localhost:5000` to browse the Markdown outputs per run.
