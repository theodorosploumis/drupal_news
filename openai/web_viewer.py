from __future__ import annotations

from pathlib import Path
from typing import List

from flask import Flask, abort, render_template_string, url_for
from markupsafe import Markup, escape
from markdown import markdown

APP = Flask(__name__)
RUNS_DIR = Path("runs")

INDEX_TEMPLATE = """
<!doctype html>
<title>Drupal Weekly Runs</title>
<style>
  body { font-family: system-ui, sans-serif; margin: 2rem; background: #f4f4f4; }
  h1 { margin-bottom: 1rem; }
  ul { list-style: none; padding: 0; }
  li { background: #fff; border-radius: 8px; margin-bottom: .75rem; padding: .75rem 1rem; }
  a { text-decoration: none; color: #005ea8; }
  a:hover { text-decoration: underline; }
  .meta { font-size: .9rem; color: #444; }
</style>
<h1>Drupal Weekly Runs</h1>
{% if runs %}
  <ul>
    {% for run in runs %}
      <li>
        <strong>{{ run }}</strong>
        <div class="meta">
          <a href="{{ url_for('show_document', run_date=run, doc='parsed') }}">parsed.md</a> ·
          <a href="{{ url_for('show_document', run_date=run, doc='summary') }}">summary.md</a> ·
          <a href="{{ url_for('show_document', run_date=run, doc='email') }}">email.txt</a>
        </div>
      </li>
    {% endfor %}
  </ul>
{% else %}
  <p>No runs found yet. Execute the pipeline to populate <code>runs/</code>.</p>
{% endif %}
"""

DOCUMENT_TEMPLATE = """
<!doctype html>
<title>{{ run_date }} · {{ filename }}</title>
<style>
  body { font-family: system-ui, sans-serif; margin: 2rem; background: #fdfdfd; }
  nav { margin-bottom: 1.5rem; }
  a { color: #005ea8; text-decoration: none; }
  a:hover { text-decoration: underline; }
  article { max-width: 920px; }
  pre { background: #f4f4f4; padding: 1rem; border-radius: 8px; overflow-x: auto; }
  table { border-collapse: collapse; width: 100%; }
  table, th, td { border: 1px solid #ddd; }
  th, td { padding: .5rem .75rem; }
  th { background: #f0f6ff; text-align: left; }
  h1 { margin-top: 0; }
</style>
<nav>
  <a href="{{ url_for('index') }}">← Back to runs</a>
</nav>
<article>
  <h1>{{ filename }} for {{ run_date }}</h1>
  {{ content|safe }}
</article>
"""


def list_runs() -> List[str]:
    if not RUNS_DIR.exists():
        return []
    runs = [p.name for p in RUNS_DIR.iterdir() if p.is_dir()]
    return sorted(runs, reverse=True)


@APP.get("/")
def index():
    return render_template_string(INDEX_TEMPLATE, runs=list_runs())


def read_md(path: Path) -> str:
    if not path.exists():
        abort(404, description=f"Document not found: {path.name}")
    return path.read_text(encoding="utf-8")


@APP.get("/runs/<run_date>/<doc>")
def show_document(run_date: str, doc: str):
    run_dir = RUNS_DIR / run_date
    if not run_dir.exists() or not run_dir.is_dir():
        abort(404, description=f"Unknown run: {run_date}")

    if doc == "parsed":
        filename = "parsed.md"
        raw = read_md(run_dir / filename)
        html = markdown(raw, extensions=["tables"])  # type: ignore[arg-type]
    elif doc == "summary":
        filename = "summary.md"
        raw = read_md(run_dir / filename)
        html = markdown(raw, extensions=["tables"])  # type: ignore[arg-type]
    elif doc == "email":
        filename = "email.txt"
        raw = read_md(run_dir / filename)
        html = f"<pre>{escape(raw)}</pre>"
    else:
        abort(404, description="Unsupported document")

    return render_template_string(
        DOCUMENT_TEMPLATE,
        run_date=run_date,
        filename=filename,
        content=Markup(html),
    )


def create_app() -> Flask:
    return APP


if __name__ == "__main__":  # pragma: no cover
    APP.run(debug=True, host="0.0.0.0", port=5000)
