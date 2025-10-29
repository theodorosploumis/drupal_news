#!/usr/bin/env python3
"""
Fix imports in src/ files to use proper package imports for drupal_news package.
"""
import os
import re
from pathlib import Path

# List of module names in the drupal_news package
MODULE_NAMES = [
    'index', 'rss_reader', 'webpage_reader', 'markdown_converter',
    'ai_summarizer', 'process_logger', 'email_sender', 'scheduler',
    'data_cleaner', 'validator', 'cache_manager', 'metrics_collector',
    'pipeline_integrity', 'viewer', 'compile_scss', 'pdf_generator',
    'cli'
]

# Patterns to fix
PATTERNS = [
    # from module_name import ...
    (r'^from (%s) import' % '|'.join(MODULE_NAMES), r'from drupal_news.\1 import'),
    # from utils.something import ...
    (r'^from (utils\.[a-z_\.]+) import', r'from drupal_news.\1 import'),
]

def fix_file(filepath):
    """Fix imports in a single file."""
    with open(filepath, 'r') as f:
        content = f.read()

    original = content

    for pattern, replacement in PATTERNS:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    src_dir = Path(__file__).parent / 'src'

    fixed_count = 0
    for py_file in src_dir.rglob('*.py'):
        if fix_file(py_file):
            print(f"Fixed: {py_file}")
            fixed_count += 1

    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()
