# Drupal Weekly News Aggregator — Implementation Specification

---

## 0. One-liner

Automated weekly Drupal aggregator: collect, normalize, cache, validate, summarize via selectable LLMs (OpenAI, Anthropic, Gemini, Ollama, LM Studio, Qwen, Grok, DeepSeek, OpenRouter), emit Markdown reports, email results, and log metrics. Timezone Europe/Athens.

---

## 1. Objectives

* Aggregate verified Drupal updates and module releases from official sources.
* Normalize and deduplicate content.
* Produce structured JSON and Markdown reports.
* Summarize content through pluggable AI models.
* Cache data to minimize redundant fetches.
* Validate and ensure reference integrity.
* Email the weekly summary with a PDF attachment.
* Collect metrics and maintain logs.

---

## 2. Scope

Timeframe: past 7 days or any user defined date ranges (Europe/Athens).

Focus areas:

1. AI and automation in/around Drupal
2. Core and major module releases
3. Canvas / new Admin UI tools
4. New modules (from [Drupal.org New Modules RSS](https://www.drupal.org/taxonomy/term/9988/feed))

Sources (examples of):

* `https://www.drupal.org`
* `https://www.drupal.org/node/3060/release/feed`
* `https://www.drupal.org/section-blog/all/feed`
* `https://www.drupal.org/project/issues/rss/ai_initiative`
* `https://www.drupal.org/taxonomy/term/9988/feed`
* `https://www.drupal.org/planet/rss.xml`

Selection rules:

* Include core updates, betas, security advisories.
* Include new contrib modules (no sandbox modules).
* Include AI/automation integrations or CI tools.
* Include Canvas/Admin UI experiments.

Output rules:

* Each fact must have a direct source link.
* Exclude duplicates and non-Drupal topics.
* Prefer `drupal.org` as canonical source.
* Ignore items with the `/sandbox/` on their URL.
* Clear factual language, no hype.
* If no major items: include “No significant core updates this week.”
* RSS entries presented as a table with `URL | Name | Description`.


---

## 3. Deliverables per run

Created under `runs/YYYY-MM-DD/`:

* `parsed.md` — raw collected data
* `summary.md` — human-readable AI summary
* `sources.json` — normalized source data
* `validation_report.json` — link and schema integrity
* `metrics.json` — run metrics and stats
* `run.log` — execution log
* `email.txt` — email body and metadata

---

## 4. Directory layout

```
drupal-weekly/
  index.py
  src/
    rss_reader.py
    webpage_reader.py
    markdown_converter.py
    ai_summarizer.py
    process_logger.py
    email_sender.py
    scheduler.py
    data_cleaner.py
    validator.py
    cache_manager.py
    metrics_collector.py
    pipeline_integrity.py
    webpage_reader.py
    utils/
      timebox.py
      dedupe.py
      html_norm.py
      io_safe.py
      schema.py
      providers/
        openai_client.py
        anthropic_client.py
        gemini_client.py
        ollama_client.py
        lmstudio_client.py
        qwen_client.py
        grok_client.py
        deepseek_client.py
        openrouter_client.py
  config.json
  providers.yaml
  .env
  requirements.txt
  README.md
  runs/
    YYYY-MM-DD/
  tests/
```

---

## 5. Configuration

### `.env`

```
TIMEZONE=Europe/Athens
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=postmaster@example.com
SMTP_PASS=REDACTED
MAIL_TO=news@example.com
MAIL_FROM=Drupal Weekly <postmaster@example.com>

OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
LMSTUDIO_BASE_URL=http://localhost:1234
QWEN_API_KEY=
GROK_API_KEY=
DEEPSEEK_API_KEY=
OPENROUTER_API_KEY=

LOG_RETENTION_DAYS=45
RUN_RETENTION_DAYS=90
CACHE_DB_PATH=./cache/cache.db
CACHE_TTL_DAYS=21
```

### `config.json`

```json
{
  "timeframe_days": 7,
  "run_root": "runs",
  "sources": {
    "rss": [
      "https://www.drupal.org/project/issues/rss/ai_initiative",
      "https://www.drupal.org/taxonomy/term/9988/feed"
    ],
    "pages": [
      "https://www.drupal.org/news",
      "https://www.drupal.org/planet",
      "https://www.drupal.org/project/drupal/releases"
    ]
  },
  "http": {
    "timeout_sec": 20,
    "retries": 2,
    "ua": "DrupalWeeklyBot/1.0"
  },
  "email": {
    "subject_prefix": "[Drupal Weekly]",
    "attach_summary": true
  },
  "markdown": {
    "table_max_rows": 200
  }
}
```

### `providers.yaml`

```yaml
default_provider: openai

providers:
  openai:
    client: openai_client
    model: gpt-4.1-mini
    temperature: 0.2

  anthropic:
    client: anthropic_client
    model: claude-3-5-sonnet
    temperature: 0.2

  gemini:
    client: gemini_client
    model: gemini-1.5-pro
    temperature: 0.2

  ollama:
    client: ollama_client
    model: qwen2.5:7b-instruct
    temperature: 0.2

  lmstudio:
    client: lmstudio_client
    model: qwen2.5:7b-instruct
    temperature: 0.2

  qwen:
    client: qwen_client
    model: qwen2.5-7b-chat
    temperature: 0.2

  grok:
    client: grok_client
    model: grok-beta
    temperature: 0.2

  deepseek:
    client: deepseek_client
    model: deepseek-chat
    temperature: 0.2

  openrouter:
    client: openrouter_client
    model: meta-llama/llama-3.1-8b-instruct
    temperature: 0.2
```

---

## 6. Pipeline modules

| Script                  | Responsibility                        |
| ----------------------- | ------------------------------------- |
| `index.py`              | Main orchestrator                     |
| `rss_reader.py`         | Fetch and normalize RSS feeds         |
| `webpage_reader.py`     | Scrape and normalize HTML pages       |
| `markdown_converter.py` | Generate `parsed.md` and `summary.md` |
| `ai_summarizer.py`      | Summarize via LLM provider            |
| `process_logger.py`     | Structured logging                    |
| `email_sender.py`       | Send email with results               |
| `scheduler.py`          | Internal weekly scheduler             |
| `data_cleaner.py`       | Rotate and compress old runs/logs     |
| `validator.py`          | Validate schema and links             |
| `cache_manager.py`      | Persistent caching with SQLite        |
| `metrics_collector.py`  | Save metrics and stats                |
| `pipeline_integrity.py` | Post-run checks and exit codes        |

---

## 7. Pipeline execution flow

1. **index.py**

   * Parse CLI args, load `.env` and config files.
   * Create `runs/YYYY-MM-DD/`.
   * Initialize logger.
2. **cache_manager.py**

   * Load or warm cache.
3. **rss_reader.py** & **webpage_reader.py**

   * Fetch and normalize content.
4. **validator.py**

   * Validate URLs, schema, and link presence.
5. **markdown_converter.py**

   * Write `parsed.md`.
6. **ai_summarizer.py**

   * Generate `summary.md` using chosen AI provider.
7. **email_sender.py**

   * Email report.
8. **metrics_collector.py**

   * Record run statistics.
9. **pipeline_integrity.py**

   * Confirm all outputs exist and match schema.
10. **data_cleaner.py**

   * Render the parsed.md and summary.md together on an HTML page
11. **viewer.py**

* Rotate logs and old runs.

---

## 8. AI summarizer details

* Dynamically loads provider module based on CLI flag.
* Fallback order: `openai → anthropic → ollama → qwen → openrouter`.
* Handles retry on truncated output.
* Supports chunked summarization if input > 200 items.
* Logs provider, model, token count, and response duration.
* Dry-run mode creates placeholder summary for testing.
* Validates `[source](...)` presence in generated Markdown.
* Exclude modules from the summary if their description starts with "Here, write an introduction that summarizes the purpose and function of this project".
* Exclude dev releases.

---

## 9. CLI usage

```
python3 index.py --provider openrouter --model mistralai/mixtral-8x7b --email yes
python3 index.py --provider qwen --model qwen2.5-7b-chat --days 7
python3 index.py --provider grok
python3 index.py --provider deepseek
```

Flags:

* `--provider` one of: openai, anthropic, gemini, ollama, lmstudio, qwen, grok, deepseek, openrouter
* `--model` overrides provider default
* `--days` set custom timeframe
* `--email yes|no` enable or skip mail sending
* `--outdir`, `--config`, `--providers`, `--env` for path overrides

---

## 10. Email

Subject: `[Drupal Weekly] YYYY-MM-DD`
Body:

```
Drupal Weekly for YYYY-MM-DD attached.
Generated at HH:MM (Europe/Athens).
Sources: drupal.org verified.
```

Attachments: `summary.md`

---

## 11. Logging and metrics

`run.log`:

```
2025-10-24T09:00:00 [index] Start
2025-10-24T09:00:30 [rss_reader] fetched=22
2025-10-24T09:01:07 [validator] passed=true
2025-10-24T09:02:05 [ai_summarizer] provider=qwen model=qwen2.5-7b-chat tokens=11234
2025-10-24T09:02:15 [email] sent to news@example.com
2025-10-24T09:02:16 [integrity] OK
2025-10-24T09:02:17 [index] exit=0
```

`metrics.json`:

```json
{
  "timestamp": "2025-10-24T23:10:00+03:00",
  "provider": "qwen",
  "model": "qwen2.5-7b-chat",
  "duration_s": 180,
  "items_total": 74,
  "tokens_used": 11890,
  "exit_code": 0
}
```

---

## 12. Scheduler (alternative to cron)

Example:

```
python3 scheduler.py --every friday --hour 9 --minute 5 --provider openai --email yes
```

Uses `apscheduler` for recurring runs.

---

## 13. Cleanup

`data_cleaner.py` automatically:

* Removes runs older than 90 days.
* Deletes logs older than 45 days.
* Compresses archived runs.
* Purges cache entries older than 21 days.

---

## 14. Validation

`validator.py` checks:

* Required keys in each JSON object.
* Valid URLs and link count > 0.
* Markdown structure integrity.
  Generates `validation_report.json`:

```json
{
  "rss_count": 40,
  "page_count": 25,
  "missing_links": 0,
  "invalid_urls": 2,
  "passed": true
}
```

---

## 15. Exit codes

| Code | Meaning                |
| ---- | ---------------------- |
| 0    | Success                |
| 10   | Partial fetch failure  |
| 20   | Validation failed      |
| 30   | Summarizer failed      |
| 40   | Email failure          |
| 50   | Integrity check failed |

---

## 16. Web Viewer

`viewer.py` provides a Flask-based web interface to browse and review aggregator results.

**Features:**
* View parsed.md and summary.md in browser
* Switch between run dates
* Tabs mode or split-view side-by-side
* View metrics and logs
* Markdown rendered to HTML with tables
* All URLs converted to clickable links opening in new tabs
* Security: `target="_blank" rel="noopener noreferrer"` on all links

**Usage:**

```bash
python3 viewer.py
# Open http://localhost:5000
```

**Routes:**
* `/` - latest run
* `/run/YYYY-MM-DD` - specific run
* `/api/runs` - list available runs (JSON)

**Link Handling:**
* Plain URLs in table cells automatically converted to `<a>` tags
* All links open in new tab with security attributes
* Prevents tab-nabbing attacks with `rel="noopener noreferrer"`

---

## 17. Requirements

```
python-dotenv>=1.0
httpx>=0.27
feedparser>=6.0
lxml>=5.3
readability-lxml>=0.8
beautifulsoup4>=4.12
python-dateutil>=2.9
pytz>=2024.1
apscheduler>=3.10
jsonschema>=4.23
sqlite-utils>=3.36
loguru>=0.7
pytest>=8.3
flask>=3.0
markdown>=3.5

Also, use venv for sandboxing.
```

Optional SDKs:

```
openai>=1.45
anthropic>=0.34
google-generativeai>=0.7
dashscope>=1.17
xai-sdk>=0.3
deepseek>=0.2
```

---

## 18. Example main structure

```python
# index.py
def main():
    logger = get_logger(run_dir)
    cache = CacheManager(config)
    rss_items = fetch_rss(config['sources']['rss'], since, tz, cache)
    page_items = fetch_pages(config['sources']['pages'], since, tz, cache)
    items = dedupe(rss_items + page_items)
    validator.validate(items)
    write_parsed_md(items, run_dir / "parsed.md")
    summary = summarize(items, provider, model, tz, days)
    write_summary_md(summary, run_dir / "summary.md")
    send_email(cfg, mail_to, subject, summary)
    metrics_collector.record(run_dir, provider, items, summary)
    ok = pipeline_integrity.verify_run(run_dir)
    sys.exit(0 if ok else 50)
```

---

## 19. Acceptance criteria

* Produces both `parsed.md` and `summary.md` with verified links.
* Summaries reproducible using any supported AI provider.
* Email sent with proper subject and attachment.
* Logs, cache, metrics, and cleanup working automatically.
* No external notifications.
* Failures surfaced only via logs and exit codes.

---

## 20. How to work

- This app is for advanced developers.
- Do not add detailed explanations on md files. Only the commands needed with a basic short explanation.
- Add a GPL-V2 licence. Get it from https://github.com/github/choosealicense.com/raw/refs/heads/gh-pages/_licenses/gpl-2.0.txt
- Add a .gitignore with the sensitive data on it so we can use git.
- Keep README.md short, no duplicates on it.

---

## 21. Summary

A modular, cron- or scheduler-ready Python system that autonomously compiles Drupal’s weekly updates, cleans itself, and works with multiple AI models including local and remote inference endpoints.
It’s reproducible, reference-linked, and silent—no external alerts, just clean artifacts and logs.
