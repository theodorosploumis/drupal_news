# Release Notes

All notable changes to Drupal News Aggregator will be documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2025-12-01

Add support for z.ai GLM-4.6 and MiniMax MiniMax-M2 providers

### New Features

**Two new Anthropic-compatible AI providers added:**

#### z.ai GLM-4.6 Provider
- New cloud provider using Anthropic-compatible endpoint
- Model: glm-4.6
- Endpoint: https://api.z.ai/api/anthropic
- API Key: ZAI_API_KEY
- Usage: drupal-news --provider zai

#### MiniMax MiniMax-M2 Provider  
- New cloud provider using Anthropic-compatible endpoint
- Model: minimax-m2
- Endpoint: https://api.minimax.io/anthropic
- API Key: MINIMAX_API_KEY
- Usage: drupal-news --provider minimax

### Implementation Details

**Configuration Updates:**
- Added provider definitions to config.yml and config.example.yml
- Both providers use anthropic_client with custom API endpoints
- Environment variable support for ZAI_API_KEY and MINIMAX_API_KEY
- No additional dependencies required (uses existing anthropic package)

**Code Changes:**
- Enhanced unified_client.py to route new providers to anthropic_client
- Enhanced anthropic_client.py to support custom API key environment variables
- Maintains full backward compatibility with existing providers

**Documentation Updates:**
- Added Anthropic-Compatible Providers section to docs/CUSTOM_API_URLS.md
- Updated config.example.yml with new provider configurations
- Created comprehensive test suite and usage guides
- Added command verification and troubleshooting documentation

### Files Added/Modified

**Modified:**
- config.yml (provider configurations - in .gitignore)
- config.example.yml (example configurations for users)
- src/utils/providers/unified_client.py (provider routing)
- src/utils/providers/anthropic_client.py (custom API key support)
- docs/CUSTOM_API_URLS.md (documentation updates)

**Created:**
- test_new_providers.py (comprehensive test suite)
- NEW_PROVIDERS_SUMMARY.md (technical documentation)
- QUICK_START_NEW_PROVIDERS.md (user guide)
- COMMAND_VERIFICATION.md (command testing verification)
- IMPLEMENTATION_COMPLETE.md (complete implementation summary)

### Testing

All tests pass successfully:
- Provider configuration validation
- Unified client routing verification
- Standalone client API key support
- CLI argument parsing
- End-to-end integration testing

### Backward Compatibility

✅ All existing providers continue to work unchanged
✅ No breaking changes introduced
✅ Zero additional dependencies
✅ Existing configurations remain valid



## [0.0.8] - 2025-11-03

Viewer improvements and styling


## [0.0.7] - 2025-11-03

Severa improvements


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
