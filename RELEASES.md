# Release Notes

All notable changes to Drupal News Aggregator will be documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.0.6] - 2025-11-03

### Refactored codebase to consolidate functionality and reduce modules

**Major refactoring to simplify codebase while maintaining all existing functionality:**

#### Consolidated Modules

- **Content Reading**: New `content_reader.py` replaces `rss_reader.py` and `webpage_reader.py` with unified interface for fetching content from both RSS feeds and web pages
- **Output Formatting**: New `output_formatter.py` replaces `markdown_converter.py` and `pdf_generator.py` with combined markdown generation and PDF conversion
- **Utilities**: New `utils/consolidated_utils.py` replaces `utils/timebox.py`, `utils/dedupe.py`, `utils/html_norm.py`, and `utils/io_safe.py` with combined time handling, deduplication, HTML normalization, and safe I/O operations
- **AI Client**: New `utils/providers/unified_client.py` replaces individual provider clients with single interface for all AI providers with fallback to specific clients

#### Module Updates

- `index.py`: Updated imports to use consolidated modules
- `ai_summarizer.py`: Updated to use unified client
- `tests/test_dedupe.py`: Updated imports to use consolidated utilities
- `tests/test_timebox.py`: Updated imports to use consolidated utilities

#### Documentation Updates

- `AGENTS.md` (formerly `CLAUDE.md`): Updated directory layout and pipeline modules sections
- `README.md`: Already reflects the new structure

#### Benefits

- Reduced complexity with fewer modules to maintain
- Improved consistency with unified interfaces for similar functionality
- Easier maintenance with changes only needed in one place
- Better organization with related functionality grouped together
- Simplified imports with cleaner import statements in main modules

#### Fixed Issues

- Resolved cache_manager import error that was causing pipeline failures
- Fixed setup.sh verification script to properly test imports


## [0.0.6] - 2025-11-03

### Refactored codebase to consolidate functionality and reduce modules

**Major refactoring to simplify codebase while maintaining all existing functionality:**

#### Consolidated Modules

- **Content Reading**: New `content_reader.py` replaces `rss_reader.py` and `webpage_reader.py` with unified interface for fetching content from both RSS feeds and web pages
- **Output Formatting**: New `output_formatter.py` replaces `markdown_converter.py` and `pdf_generator.py` with combined markdown generation and PDF conversion
- **Utilities**: New `utils/consolidated_utils.py` replaces `utils/timebox.py`, `utils/dedupe.py`, `utils/html_norm.py`, and `utils/io_safe.py` with combined time handling, deduplication, HTML normalization, and safe I/O operations
- **AI Client**: New `utils/providers/unified_client.py` replaces individual provider clients with single interface for all AI providers with fallback to specific clients

#### Module Updates

- `index.py`: Updated imports to use consolidated modules
- `ai_summarizer.py`: Updated to use unified client
- `tests/test_dedupe.py`: Updated imports to use consolidated utilities
- `tests/test_timebox.py`: Updated imports to use consolidated utilities

#### Documentation Updates

- `AGENTS.md` (formerly `CLAUDE.md`): Updated directory layout and pipeline modules sections
- `README.md`: Already reflects the new structure

#### Benefits

- Reduced complexity with fewer modules to maintain
- Improved consistency with unified interfaces for similar functionality
- Easier maintenance with changes only needed in one place
- Better organization with related functionality grouped together
- Simplified imports with cleaner import statements in main modules

#### Fixed Issues

- Resolved cache_manager import error that was causing pipeline failures
- Fixed setup.sh verification script to properly test imports

## [0.0.5] - 2025-10-30

Fix viewer, add smtp key on config.yaml


## [0.0.4] - 2025-10-30

Fixing ua missing key


## [0.0.3] - 2025-10-30

Unify config files into a single yaml file.


## [0.0.2] - 2025-10-29

Release v0.0.2


## [0.0.1] - 2025-10-29

Initial


## Future Releases

See [GitHub Releases](https://github.com/theodorosploumis/drupal_news/releases) for upcoming versions.
