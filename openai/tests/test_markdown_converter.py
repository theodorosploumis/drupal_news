from datetime import datetime

import pytz

from src.markdown_converter import build_parsed_markdown, write_summary_pdf


def test_markdown_contains_rss_table():
    tz = pytz.timezone("Europe/Athens")
    now = datetime.now(tz)
    items = [
        {
            "title": "Drupal 11.0 released",
            "url": "https://www.drupal.org/project/drupal/releases/11.0",
            "summary": "Core release",
            "published": now.isoformat(),
            "source": "https://www.drupal.org/project/drupal/releases",
            "kind": "rss",
        }
    ]
    md = build_parsed_markdown(items, now, now, "Europe/Athens")
    assert "| URL | Name | Short description |" in md
    assert "Drupal 11.0 released" in md


def test_write_summary_pdf(tmp_path):
    summary = "# Heading\n\nSome content with a table.\n\n| A | B |\n| - | - |\n| 1 | 2 |"
    pdf_path = tmp_path / "summary.pdf"
    write_summary_pdf(pdf_path, summary)
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 100
