# Release Notes

All notable changes to Drupal News Aggregator will be documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2025-10-29

### Added
- Initial release of Drupal News Aggregator
- Multi-provider AI support (OpenAI, Anthropic, Gemini, Ollama, LMStudio, Qwen, Grok, DeepSeek, OpenRouter)
- Generic provider support for any OpenAI-compatible API
- RSS feed aggregation from drupal.org
- Web page scraping for Drupal news
- Custom CSS selector support for page scraping
- AI-powered summarization with configurable prompts
- Email delivery with PDF attachments
- Web viewer with tabs and split-view modes
- SQLite caching to reduce redundant fetches
- Comprehensive validation and integrity checks
- Metrics collection and cost tracking
- Automated cleanup of old runs and logs
- Scheduler for recurring runs
- CLI tools: drupal-news, drupal-news-scheduler, drupal-news-email, drupal-news-viewer
- Comprehensive documentation
- PyPI package distribution
- Support for custom provider configurations (LiteLLM, Portkey, etc.)
- SCSS compilation for web viewer
- Markdown to PDF conversion
- Exit codes for CI/CD integration

### Changed
- Renamed project from drupal-weekly to drupal-news
- Updated all references from "weekly" to "news" terminology
- Updated user agent to DrupalNewsBot/1.0

### Fixed
- Import paths after package restructuring
- Provider configuration validation
- Cache key generation for consistency

## Future Releases

See [GitHub Releases](https://github.com/yourusername/drupal-news/releases) for upcoming versions.
