#!/usr/bin/env python3
"""
CLI entry points for drupal-news package.
"""
import sys

from drupal_news.version import get_current_version


def main():
    """Main CLI entry point for drupal-news command."""
    if "--version" in sys.argv:
        print(f"drupal-news version {get_current_version()}")
        sys.exit(0)
    from drupal_news.index import main as index_main
    sys.exit(index_main())


def scheduler_main():
    """Scheduler CLI entry point for drupal-news-scheduler command."""
    if "--version" in sys.argv:
        print(f"drupal-news-scheduler version {get_current_version()}")
        sys.exit(0)
    from drupal_news.scheduler import main as scheduler_main_func
    sys.exit(scheduler_main_func())


def email_main():
    """Email CLI entry point for drupal-news-email command."""
    if "--version" in sys.argv:
        print(f"drupal-news-email version {get_current_version()}")
        sys.exit(0)
    from drupal_news.email_sender import main as email_main_func
    sys.exit(email_main_func())


def viewer_main():
    """Web viewer CLI entry point for drupal-news-viewer command."""
    import argparse
    from drupal_news.viewer import app

    if '--version' in sys.argv:
        print(f"drupal-news-viewer version {get_current_version()}")
        sys.exit(0)

    parser = argparse.ArgumentParser(description="Drupal News Viewer")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on (default: 5000)")
    args = parser.parse_args()

    print("=" * 60)
    print("Drupal News Viewer")
    print("=" * 60)
    print(f"Starting server on http://localhost:{args.port}")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    app.run(debug=False, host='0.0.0.0', port=args.port)


if __name__ == "__main__":
    main()
