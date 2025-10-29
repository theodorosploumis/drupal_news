"""PDF generator for Drupal Aggregator summaries."""
from pathlib import Path
from typing import Optional
import markdown


def markdown_to_pdf(
    markdown_path: Path,
    pdf_path: Path,
    title: Optional[str] = None,
    css_style: Optional[str] = None
) -> bool:
    """
    Convert markdown file to PDF.

    Args:
        markdown_path: Path to input markdown file
        pdf_path: Path to output PDF file
        title: Optional document title
        css_style: Optional custom CSS styles

    Returns:
        True if successful, False otherwise
    """
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
    except ImportError:
        print("Error: weasyprint not installed. Install with: pip install weasyprint")
        return False

    try:
        # Read markdown content
        with open(markdown_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Convert markdown to HTML
        md = markdown.Markdown(extensions=[
            'extra',
            'codehilite',
            'tables',
            'toc',
            'fenced_code'
        ])
        html_body = md.convert(md_content)

        # Get title from metadata or use provided title
        doc_title = title or "Drupal Aggregator Summary"

        # Default CSS styling
        default_css = """
        @page {
            size: A4;
            margin: 2cm;
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 9pt;
                color: #666;
            }
        }

        body {
            font-family: "DejaVu Sans", Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
        }

        h1 {
            color: #0678BE;
            font-size: 24pt;
            margin-top: 0;
            margin-bottom: 0.5em;
            border-bottom: 2px solid #0678BE;
            padding-bottom: 0.3em;
        }

        h2 {
            color: #0678BE;
            font-size: 18pt;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            border-bottom: 1px solid #ccc;
            padding-bottom: 0.2em;
        }

        h3 {
            color: #333;
            font-size: 14pt;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }

        h4, h5, h6 {
            color: #555;
            margin-top: 0.8em;
            margin-bottom: 0.4em;
        }

        p {
            margin: 0.5em 0;
            text-align: justify;
        }

        a {
            color: #0678BE;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        ul, ol {
            margin: 0.5em 0;
            padding-left: 2em;
        }

        li {
            margin: 0.3em 0;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
            font-size: 10pt;
        }

        th {
            background-color: #0678BE;
            color: white;
            font-weight: bold;
            padding: 8px;
            text-align: left;
            border: 1px solid #ddd;
        }

        td {
            padding: 6px 8px;
            border: 1px solid #ddd;
        }

        tr:nth-child(even) {
            background-color: #f9f9f9;
        }

        code {
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: "DejaVu Sans Mono", monospace;
            font-size: 9pt;
        }

        pre {
            background-color: #f4f4f4;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 3px solid #0678BE;
        }

        pre code {
            background-color: transparent;
            padding: 0;
        }

        blockquote {
            border-left: 4px solid #0678BE;
            margin: 1em 0;
            padding-left: 1em;
            color: #666;
            font-style: italic;
        }

        hr {
            border: none;
            border-top: 1px solid #ccc;
            margin: 2em 0;
        }

        .metadata {
            background-color: #f9f9f9;
            padding: 1em;
            border-radius: 5px;
            margin-bottom: 2em;
            font-size: 9pt;
            color: #666;
        }
        """

        # Use custom CSS if provided, otherwise use default
        final_css = css_style or default_css

        # Create full HTML document
        html_doc = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{doc_title}</title>
        </head>
        <body>
            {html_body}
        </body>
        </html>
        """

        # Configure fonts
        font_config = FontConfiguration()

        # Generate PDF
        HTML(string=html_doc).write_pdf(
            pdf_path,
            stylesheets=[CSS(string=final_css, font_config=font_config)],
            font_config=font_config
        )

        return True

    except Exception as e:
        print(f"PDF generation failed: {e}")
        return False


def generate_summary_pdf(
    run_dir: Path,
    markdown_filename: str = "summary.md",
    pdf_filename: str = "summary.pdf",
    period_label: str = "Weekly"
) -> Optional[Path]:
    """
    Generate PDF from summary markdown in run directory.

    Args:
        run_dir: Run directory path
        markdown_filename: Name of markdown file (default: summary.md)
        pdf_filename: Name of output PDF file (default: summary.pdf)
        period_label: Period label (e.g., "Weekly", "Biweekly")

    Returns:
        Path to generated PDF, or None if failed
    """
    markdown_path = run_dir / markdown_filename
    pdf_path = run_dir / pdf_filename

    if not markdown_path.exists():
        print(f"Error: Markdown file not found: {markdown_path}")
        return None

    # Extract title from run directory name
    title = f"Drupal {period_label} Summary - {run_dir.name}"

    if markdown_to_pdf(markdown_path, pdf_path, title=title):
        return pdf_path
    else:
        return None
