#!/usr/bin/env python3
"""
Web viewer for Drupal Weekly News Aggregator results.
Renders parsed.md and summary.md in a browser interface.
"""
import os
import sys
import re
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request
import markdown

app = Flask(__name__)

# Configuration
RUN_ROOT = Path(__file__).parent / "runs"


def get_available_runs():
    """Get list of available run directories."""
    if not RUN_ROOT.exists():
        return []
    runs = [d.name for d in RUN_ROOT.iterdir() if d.is_dir()]
    return sorted(runs, reverse=True)


def read_markdown_file(run_date, filename):
    """Read markdown file and convert to HTML."""
    file_path = RUN_ROOT / run_date / filename
    if not file_path.exists():
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

    # Convert plain URLs in table cells to links
    def linkify_url(match):
        url = match.group(1)
        return f'<td><a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a></td>'

    html_content = re.sub(
        r'<td>(https?://[^<]+)</td>',
        linkify_url,
        html_content
    )

    # Add target="_blank" to all existing links
    html_content = re.sub(
        r'<a\s+([^>]*?)href=',
        r'<a \1target="_blank" rel="noopener noreferrer" href=',
        html_content
    )

    return html_content


def read_json_file(run_date, filename):
    """Read JSON file."""
    file_path = RUN_ROOT / run_date / filename
    if not file_path.exists():
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Drupal Weekly Viewer - {{ run_date }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        header {
            background: #0678be;
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        header h1 {
            font-size: 1.5rem;
            font-weight: 500;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        .controls {
            background: white;
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .controls select {
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1rem;
        }
        .tabs {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        .tab {
            background: white;
            border: none;
            padding: 0.75rem 1.5rem;
            cursor: pointer;
            border-radius: 4px 4px 0 0;
            font-size: 1rem;
            transition: background 0.2s;
        }
        .tab:hover {
            background: #f0f0f0;
        }
        .tab.active {
            background: #0678be;
            color: white;
        }
        .content {
            background: white;
            padding: 2rem;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            min-height: 500px;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        ul, ol {
            list-style-position: inside;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
        }
        tr:hover {
            background: #f8f9fa;
        }
        a {
            color: #0678be;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        h1, h2, h3 {
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
        h1 { font-size: 2rem; }
        h2 { font-size: 1.5rem; color: #0678be; }
        h3 { font-size: 1.25rem; }
        code {
            background: #f4f4f4;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: "Courier New", monospace;
        }
        pre {
            background: #f4f4f4;
            padding: 1rem;
            border-radius: 4px;
            overflow-x: auto;
            margin: 1rem 0;
        }
        .no-data {
            text-align: center;
            color: #999;
            padding: 3rem;
            font-size: 1.1rem;
        }
        .view-mode {
            display: flex;
            gap: 0.5rem;
        }
        .view-mode button {
            padding: 0.5rem 1rem;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            border-radius: 4px;
        }
        .view-mode button.active {
            background: #0678be;
            color: white;
            border-color: #0678be;
        }
        .split-view {
            display: none;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        .split-view.active {
            display: grid;
        }
        .split-panel {
            background: white;
            padding: 2rem;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow-y: auto;
            max-height: 80vh;
        }
        .split-panel h2:first-child {
            margin-top: 0;
            border-bottom: 2px solid #0678be;
            padding-bottom: 0.5rem;
        }
    </style>
</head>
<body>
    <header>
        <h1>🐘 Drupal Weekly News Viewer</h1>
    </header>

    <div class="container">
        <div class="controls">
            <div>
                <label for="run-select">Select Run: </label>
                <select id="run-select" onchange="changeRun(this.value)">
                    {% for run in runs %}
                    <option value="{{ run }}" {% if run == run_date %}selected{% endif %}>{{ run }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="view-mode">
                <button onclick="setViewMode('tabs')" class="active" id="tabs-btn">Tabs</button>
                <button onclick="setViewMode('split')" id="split-btn">Split View</button>
            </div>
        </div>

        <div id="tabs-view" class="active">
            <div class="tabs">
                <button class="tab active" onclick="showTab('summary')">Summary</button>
                <button class="tab" onclick="showTab('parsed')">Parsed Data</button>
                <button class="tab" onclick="showTab('metrics')">Metrics</button>
                <button class="tab" onclick="showTab('log')">Log</button>
            </div>

            <div class="content">
                <div id="summary-content" class="tab-content active">
                    {% if summary %}
                        {{ summary|safe }}
                    {% else %}
                        <div class="no-data">Summary not available</div>
                    {% endif %}
                </div>

                <div id="parsed-content" class="tab-content">
                    {% if parsed %}
                        {{ parsed|safe }}
                    {% else %}
                        <div class="no-data">Parsed data not available</div>
                    {% endif %}
                </div>

                <div id="metrics-content" class="tab-content">
                    {% if metrics %}
                        <h2>Run Metrics</h2>
                        <pre>{{ metrics }}</pre>
                    {% else %}
                        <div class="no-data">Metrics not available</div>
                    {% endif %}
                </div>

                <div id="log-content" class="tab-content">
                    {% if log %}
                        <h2>Run Log</h2>
                        <pre>{{ log }}</pre>
                    {% else %}
                        <div class="no-data">Log not available</div>
                    {% endif %}
                </div>
            </div>
        </div>

        <div id="split-view" class="split-view">
            <div class="split-panel">
                <h2>Summary</h2>
                {% if summary %}
                    {{ summary|safe }}
                {% else %}
                    <div class="no-data">Summary not available</div>
                {% endif %}
            </div>
            <div class="split-panel">
                <h2>Parsed Data</h2>
                {% if parsed %}
                    {{ parsed|safe }}
                {% else %}
                    <div class="no-data">Parsed data not available</div>
                {% endif %}
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });

            // Show selected tab content
            document.getElementById(tabName + '-content').classList.add('active');

            // Add active class to clicked tab
            event.target.classList.add('active');
        }

        function changeRun(runDate) {
            window.location.href = '/run/' + runDate;
        }

        function setViewMode(mode) {
            document.querySelectorAll('.view-mode button').forEach(btn => {
                btn.classList.remove('active');
            });

            if (mode === 'tabs') {
                document.getElementById('tabs-view').classList.add('active');
                document.getElementById('split-view').classList.remove('active');
                document.getElementById('tabs-btn').classList.add('active');
            } else {
                document.getElementById('tabs-view').classList.remove('active');
                document.getElementById('split-view').classList.add('active');
                document.getElementById('split-btn').classList.add('active');
            }
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Show latest run."""
    runs = get_available_runs()
    if not runs:
        return "<h1>No runs available</h1><p>Run the aggregator first to generate data.</p>"

    return view_run(runs[0])


@app.route('/run/<run_date>')
def view_run(run_date):
    """View specific run."""
    runs = get_available_runs()
    if run_date not in runs:
        return f"<h1>Run not found: {run_date}</h1>", 404

    summary_html = read_markdown_file(run_date, 'summary.md')
    parsed_html = read_markdown_file(run_date, 'parsed.md')
    metrics_json = read_json_file(run_date, 'metrics.json')
    log_text = read_json_file(run_date, 'run.log')

    return render_template_string(
        HTML_TEMPLATE,
        run_date=run_date,
        runs=runs,
        summary=summary_html,
        parsed=parsed_html,
        metrics=metrics_json,
        log=log_text
    )


@app.route('/api/runs')
def api_runs():
    """API endpoint to list all runs."""
    runs = get_available_runs()
    return jsonify(runs)


if __name__ == '__main__':
    print("=" * 60)
    print("Drupal Weekly News Viewer")
    print("=" * 60)
    print(f"Run root: {RUN_ROOT}")
    print(f"Available runs: {len(get_available_runs())}")
    print("\nStarting server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
