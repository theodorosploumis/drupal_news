"""Version helpers for drupal_news."""

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


PACKAGE_NAME = "drupal-news"


def get_current_version() -> str:
    """Return installed package version, with file fallback for local checkouts."""
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        version_file = Path(__file__).resolve().parent.parent / "VERSION"
        if version_file.exists():
            return version_file.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return "unknown"
