#!/usr/bin/env python3
"""Test script to verify the refactored code works correctly."""

import sys
from pathlib import Path

# Add src to path so we can import drupal_news modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all the refactored modules can be imported correctly."""
    try:
        # Test importing consolidated modules
        from drupal_news.content_reader import fetch_content
        from drupal_news.output_formatter import write_parsed_md, write_summary_md, generate_summary_pdf
        from drupal_news.utils.consolidated_utils import dedupe_items, days_ago, now_in_tz
        from drupal_news.utils.providers.unified_client import generate_summary

        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_unified_client():
    """Test that the unified client can be imported."""
    try:
        from drupal_news.utils.providers.unified_client import generate_summary
        print("✓ Unified client imported successfully")
        return True
    except Exception as e:
        print(f"✗ Unified client import failed: {e}")
        return False

def test_consolidated_utils():
    """Test that consolidated utilities work."""
    try:
        from drupal_news.utils.consolidated_utils import dedupe_items, days_ago
        from datetime import datetime

        # Test deduplication
        items = [
            {"title": "Test 1", "url": "https://example.com/1"},
            {"title": "Test 1", "url": "https://example.com/1"},  # Duplicate
            {"title": "Test 2", "url": "https://example.com/2"},
        ]

        unique = dedupe_items(items)
        assert len(unique) == 2, f"Expected 2 unique items, got {len(unique)}"

        # Test time functions
        past = days_ago(7)
        now = datetime.now(past.tzinfo)
        assert past < now, "Days ago should be before now"

        print("✓ Consolidated utilities work correctly")
        return True
    except Exception as e:
        print(f"✗ Consolidated utilities test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing refactored code...")

    tests = [
        test_imports,
        test_unified_client,
        test_consolidated_utils
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1

    print(f"\n{passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)