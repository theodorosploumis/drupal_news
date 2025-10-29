# Drupal News Aggregator Monorepo

This repository hosts a provider-agnostic automation pipeline that assembles the past week's Drupal announcements, module releases, and AI-related initiatives into structured reports. Each provider directory (for example `openai/`, `claude/`, `grok/`, `q/`, `opcode/`) packages the same core workflow with the credentials, SDK clients, and configuration required for that large language model or API.

## Key Capabilities
- Collects curated RSS feeds and canonical Drupal pages, constrained to the last seven days in the Europe/Athens timezone.
- Normalises, deduplicates, and validates entries before promotion to the final report set.
- Generates Markdown, JSON, PDF, and email-ready artifacts per run under `runs/YYYY-MM-DD/`.
- Exposes a pluggable summarisation layer so different AI providers can produce human-friendly highlights.
- Persists cache data and run metrics to reduce repeated downloads and aid observability.

## Repository Layout
- `specification.md` — project requirements, objectives, and architectural expectations.
- `openai/`, `claude/`, `grok/`, `opcode/`, `q/` — provider-specific implementations built on the shared spec.
- `runs/` (inside each provider package) — dated execution outputs (`parsed.md`, `summary.md`, `sources.json`, `metrics.json`, etc.).
- `utils/`, `src/`, `tests/` — live under each provider directory and include the ingestion pipeline, adapters, helpers, and automated tests.

## Getting Started
1. Pick a provider directory that matches the LLM service you plan to use (for instance `openai/`).
2. Follow that directory's `README.md` for environment setup, dependency installation, and CLI usage.
3. Create a `.env` (or provider-specific variant) with API keys, email settings, and scheduling parameters.
4. Run the entrypoint (typically `python -m src.index --provider <name>`). Optional schedulers, PDF/email exporters, and web viewers are documented in the provider README files.

## Operational Notes
- Outputs are organised per execution date and include validation reports to help catch broken links or schema drift.
- The pipeline favours Drupal.org links and omits sandbox modules or non-Drupal content by design.
- If no qualifying news is found for a period, the summary explicitly states the absence of major updates.

Refer to `specification.md` for deeper architectural guidance and implementation commitments across providers.

## License
[GPL v2][LICENSE]
