# Drupal News Aggregator

Automated Drupal news aggregation with AI summarization.

## Quick Start

```bash
./setup.sh
source venv/bin/activate
python3 index.py --dry-run
```

## Configuration

### Environment Variables (.env)

```bash
TIMEZONE=Europe/Athens
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASS=password
MAIL_TO=recipient@example.com
MAIL_FROM=sender@example.com
```

### News Sources (config.json)

Edit `config.json` in the root directory to manage RSS feeds and web pages.

### AI Summarizer Prompt (prompt.md)

Edit `prompt.md` in the root directory to customize the AI summarization prompt:

```markdown
# Requirements
1. Focus on: AI module and news on AI
2. Each fact MUST include a [source](URL) link
3. Use clear, factual language - no hype
...
```

**Note:** If `prompt.md` is not found, the system uses a hardcoded default template.

### AI Providers (providers.yaml)

Configure AI models in `providers.yaml`

## Usage

```bash
# Basic
python3 index.py --provider openai --days 7

# Test
python3 index.py --dry-run --verbose

# Schedule
python3 scheduler.py --every friday --hour 9 --provider openai

# Cron
0 9 * * 5 cd /path && python3 index.py --provider openai
```

## Web Viewer

```bash
python3 viewer.py
# Open http://localhost:5000
```

Features: tabs/split view, run history, metrics, logs

## Providers

Built-in: OpenAI, Anthropic, Gemini, Ollama, LMStudio, Qwen, Grok, DeepSeek, OpenRouter

**Generic:** Works with ANY OpenAI-compatible API (OpenRouter, Together AI, Groq, Perplexity, Fireworks, Azure OpenAI, custom endpoints)

See: [Generic Provider Guide](docs/GENERIC_PROVIDER.md)

## CLI Flags

```bash
--provider 	<name>     AI provider
--model 	<name>     Override model
--days 		 <n>       Timeframe (default: 7)
--email 	yes|no     Send email
--dry-run              Skip AI/email
--verbose              Debug output
--config 	<path>     Custom config.json
--providers <path>     Custom providers.yaml
--env 		<path>     Custom .env
--outdir 	<path>     Custom output directory
```

## Output

`runs/YYYY-MM-DD/`: parsed.md, summary.md, sources.json, metrics.json, run.log

## Structure

```
├── setup.sh        # Setup script
├── index.py        # Main entry
├── scheduler.py    # Scheduler
├── viewer.py       # Web viewer
├── src/            # Source code
├── venv/           # Virtual env
├── config.json     # Config
├── providers.yaml  # AI providers
├── prompt.md       # AI summarizer prompt (optional)
└── .env            # Credentials
```

## Exit Codes

-  0: Success
- 10: Partial fetch failure
- 20: Validation failed
- 30: Summarizer failed
- 40: Email failure
- 50: Integrity check failed

## License

GPL-V2
