#!/usr/bin/env python3
"""
Rename drupal-weekly to drupal-news throughout the project.
Replaces 'weekly' with 'news' in files, directories, and content.
"""
import os
import re
from pathlib import Path

# Mapping of old to new names
REPLACEMENTS = {
    'drupal-weekly': 'drupal-news',
    'drupal_weekly': 'drupal_news',
    'Drupal Weekly': 'Drupal News',
    'drupal weekly': 'drupal news',
    'weekly': 'news',
    'Weekly': 'News',
    'WEEKLY': 'NEWS',
}

# Files and directories to process
FILES_TO_PROCESS = [
    'pyproject.toml',
    'build_package.py',
    'setup.sh',
    'README.md',
    'CLAUDE.md',
    '.env.example',
    'config.json',
    'config.example.json',
    'providers.yaml',
    'Makefile',
    'fix_imports.py',
    'src/cli.py',
    'src/index.py',
    'src/email_sender.py',
    'src/scheduler.py',
    'src/viewer.py',
    'docs/PACKAGING.md',
    'docs/USAGE.md',
]

def replace_in_file(filepath):
    """Replace text in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # Apply replacements in order (most specific first)
        for old, new in REPLACEMENTS.items():
            content = content.replace(old, new)

        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    root = Path(__file__).parent
    os.chdir(root)

    print("Renaming drupal-weekly to drupal-news...")
    print("=" * 60)

    fixed_count = 0

    for file_path in FILES_TO_PROCESS:
        full_path = root / file_path
        if full_path.exists():
            if replace_in_file(full_path):
                print(f"✓ Updated: {file_path}")
                fixed_count += 1
            else:
                print(f"  No changes: {file_path}")
        else:
            print(f"  Not found: {file_path}")

    print("=" * 60)
    print(f"Updated {fixed_count} files")
    print("\nNext steps:")
    print("1. Rebuild package: python3 build_package.py --clean --build")
    print("2. Test installation: python3 build_package.py --test")

if __name__ == '__main__':
    main()
