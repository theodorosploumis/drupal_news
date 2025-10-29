"""Safe I/O utilities for Drupal Aggregator."""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists, create if needed."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_write_json(data: Any, filepath: Path, indent: int = 2) -> bool:
    """Safely write JSON to file."""
    try:
        filepath = Path(filepath)
        ensure_dir(filepath.parent)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error writing JSON to {filepath}: {e}")
        return False


def safe_read_json(filepath: Path) -> Optional[Dict[str, Any]]:
    """Safely read JSON from file."""
    try:
        filepath = Path(filepath)
        if not filepath.exists():
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON from {filepath}: {e}")
        return None


def safe_write_text(text: str, filepath: Path, encoding: str = 'utf-8') -> bool:
    """Safely write text to file."""
    try:
        filepath = Path(filepath)
        ensure_dir(filepath.parent)

        with open(filepath, 'w', encoding=encoding) as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"Error writing text to {filepath}: {e}")
        return False


def safe_read_text(filepath: Path, encoding: str = 'utf-8') -> Optional[str]:
    """Safely read text from file."""
    try:
        filepath = Path(filepath)
        if not filepath.exists():
            return None

        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"Error reading text from {filepath}: {e}")
        return None


def safe_read_yaml(filepath: Path) -> Optional[Dict[str, Any]]:
    """Safely read YAML from file."""
    try:
        filepath = Path(filepath)
        if not filepath.exists():
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading YAML from {filepath}: {e}")
        return None


def file_exists(filepath: Path) -> bool:
    """Check if file exists."""
    return Path(filepath).exists()


def get_file_size(filepath: Path) -> int:
    """Get file size in bytes."""
    try:
        return Path(filepath).stat().st_size
    except Exception:
        return 0


def list_files(directory: Path, pattern: str = "*") -> list:
    """List files in directory matching pattern."""
    try:
        directory = Path(directory)
        if not directory.exists():
            return []
        return list(directory.glob(pattern))
    except Exception:
        return []
