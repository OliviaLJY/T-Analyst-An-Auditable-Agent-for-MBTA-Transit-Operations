"""Render a self-contained HTML evaluation report from a JSON result file."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


def escape(value: Any) -> str:
    return html.escape(str(value))


def status(value: bool, true_label: str = "Valid", false_label: str = "Invalid") -> str:
    css_class = "pass" if value else "fail"
    label = true_label if value else false_label
    return f'<span class="status {css_class}">{escape(label)}</span>'


def render_card(result: dict[str, Any], index: int) -> str:
    fallback = bool(result["fallback_triggered"])
    searchable = " ".join(
        [
            result["id"],
            result["category"],
            result["question"],
            result["expected_calls"],
            result["selected_calls"],
            result["answer"],
        ]
    ).casefold()
    return f"""
    <article
      class="case-card"
      data-category="{escape(result["category"])}"
      data-search="{escape(searchable)}"
    >
      <div class="case-heading">
        <div>
          <span class="case-number">Case {index:02d}</span>
          <span class="category">{escape(result["category"])}</span>
        </div>
        {status(result["passed"], "Passed", "Failed")}
      </div>
      <h2>{escape(result["question"])}</h2>
      <div class="tool-grid">
        <div>
          <p class="label">Expected tool</p>
          <code>{escape(result["expected_calls"])}</code>
        </div>
        <div>
          <p class="label">Selected tool</p>
          <code>{escape(result["selected_calls"])}</code>
        </div>
      </div>
      <div class="checks">
        <div><span>Tool selection</span>{status(result["tool_selection_correct"], "Correct", "Incorrect")}</div>
        <div><span>Result</span>{status(result["result_valid"])}</div>
        <div><span>Citation</span>{status(result["citation_valid"])}</div>
        <div><span>Fallback</span>{status(not fallback, "No", "Yes")}</div>
      </div>
      <div class="answer">
        <p class="label">Final answer</p>
        <p>{escape(result["answer"])}</p>
      </div>
    </article>
    """


def render_report(report: dict[str, Any]) -> str:
    summary = report["summary"]
    results = report["results"]
    categories = sorted({result["category"] for result in results})
    category_options = "\n".join(
        f'<option value="{escape(category)}">{escape(category.title())}</option>'
        for category in categories
    )
    cards = "\n".join(
        render_card(result, index) for index, result in enumerate(results, start=1)
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="T-Analyst agent evaluation results">
  <title>T-Analyst Evaluation Report</title>
  <style>
    :root {{
      --navy: #102a43;
      --blue: #2f6f8f;
      --teal: #0f766e;
      --green: #147d64;
      --red: #b42318;
      --ink: #243b53;
      --muted: #627d98;
      --line: #d9e2ec;
      --surface: #ffffff;
      --background: #f4f7fa;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--background);
      font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    header {{
      color: white;
      background:
        radial-gradient(circle at 90% 10%, rgba(45, 212, 191, .2), transparent 28rem),
        linear-gradient(130deg, #102a43, #164e63);
      padding: 4.5rem 1.25rem 5.5rem;
    }}
    .container {{ width: min(1120px, calc(100% - 2rem)); margin: 0 auto; }}
    .eyebrow {{
      margin: 0 0 .7rem;
      color: #99f6e4;
      font-size: .77rem;
      font-weight: 800;
      letter-spacing: .13em;
      text-transform: uppercase;
    }}
    h1 {{ max-width: 760px; margin: 0; font-size: clamp(2.1rem, 6vw, 4rem); line-height: 1.04; }}
    .intro {{ max-width: 700px; margin: 1rem 0 0; color: #d9e2ec; font-size: 1.05rem; }}
    .meta {{ margin-top: 1.25rem; color: #bcccdc; font-size: .86rem; }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: .9rem;
      margin-top: -2.2rem;
    }}
    .metric {{
      min-height: 116px;
      padding: 1.2rem;
      border: 1px solid var(--line);
      border-radius: 15px;
      background: var(--surface);
      box-shadow: 0 10px 30px rgba(16, 42, 67, .08);
    }}
    .metric strong {{ display: block; color: var(--navy); font-size: 1.8rem; line-height: 1.15; }}
    .metric span {{ display: block; margin-top: .45rem; color: var(--muted); font-size: .82rem; }}
    main {{ padding: 2.3rem 0 4rem; }}
    .controls {{
      display: grid;
      grid-template-columns: 1fr 260px;
      gap: .8rem;
      margin: .5rem 0 1.2rem;
    }}
    input, select {{
      width: 100%;
      padding: .8rem .9rem;
      border: 1px solid #bcccdc;
      border-radius: 10px;
      color: var(--ink);
      background: white;
      font: inherit;
    }}
    input:focus, select:focus {{ outline: 3px solid rgba(47, 111, 143, .18); border-color: var(--blue); }}
    #visible-count {{ margin: 0 0 1rem; color: var(--muted); font-size: .85rem; }}
    .case-card {{
      margin-bottom: 1rem;
      padding: 1.4rem;
      border: 1px solid var(--line);
      border-radius: 15px;
      background: var(--surface);
      box-shadow: 0 4px 16px rgba(16, 42, 67, .045);
    }}
    .case-card[hidden] {{ display: none; }}
    .case-heading, .checks > div {{ display: flex; align-items: center; justify-content: space-between; gap: .75rem; }}
    .case-number {{ color: var(--muted); font-size: .76rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }}
    .category {{
      display: inline-block;
      margin-left: .55rem;
      padding: .2rem .52rem;
      border-radius: 999px;
      color: #0e4f4a;
      background: #ccfbf1;
      font-size: .74rem;
      font-weight: 700;
    }}
    h2 {{ margin: .85rem 0 1rem; color: var(--navy); font-size: 1.22rem; line-height: 1.35; }}
    .tool-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; }}
    .tool-grid > div, .answer {{
      min-width: 0;
      padding: .85rem;
      border: 1px solid #e6edf3;
      border-radius: 10px;
      background: #f8fafc;
    }}
    .label {{ margin: 0 0 .35rem; color: var(--muted); font-size: .72rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }}
    code {{ color: #0b5563; font-size: .78rem; overflow-wrap: anywhere; }}
    .checks {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: .65rem;
      margin: .8rem 0;
    }}
    .checks > div {{ padding: .65rem .7rem; border-radius: 9px; background: #eef3f7; font-size: .78rem; }}
    .status {{ display: inline-flex; align-items: center; gap: .3rem; font-size: .73rem; font-weight: 800; white-space: nowrap; }}
    .status::before {{ width: .48rem; height: .48rem; border-radius: 50%; content: ""; background: currentColor; }}
    .status.pass {{ color: var(--green); }}
    .status.fail {{ color: var(--red); }}
    .answer p:last-child {{ margin: 0; white-space: pre-wrap; font-size: .9rem; }}
    footer {{ padding: 0 0 3rem; color: var(--muted); font-size: .8rem; text-align: center; }}
    @media (max-width: 820px) {{
      header {{ padding-top: 3rem; }}
      .summary {{ grid-template-columns: repeat(2, 1fr); }}
      .controls, .tool-grid {{ grid-template-columns: 1fr; }}
      .checks {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    @media (max-width: 480px) {{
      .summary, .checks {{ grid-template-columns: 1fr; }}
      .metric {{ min-height: 0; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="container">
      <p class="eyebrow">T-Analyst · Agent evaluation</p>
      <h1>Can the agent choose, compute, and cite correctly?</h1>
      <p class="intro">A case-by-case report for the fixed English evaluation suite, using deterministic transit tools and Parley GPT-5.5.</p>
      <p class="meta">Run: {escape(report["run_at"])} · Model: {escape(report["model"])}</p>
    </div>
  </header>

  <div class="container summary" aria-label="Evaluation summary">
    <div class="metric"><strong>{summary["total"]}</strong><span>cases</span></div>
    <div class="metric"><strong>{summary["tool_selection_correct"]}/{summary["total"]}</strong><span>tool selection</span></div>
    <div class="metric"><strong>{summary["result_valid"]}/{summary["total"]}</strong><span>usable results</span></div>
    <div class="metric"><strong>{summary["citation_valid"]}/{summary["total"]}</strong><span>valid citations</span></div>
    <div class="metric"><strong>{summary["fallback_triggered"]}</strong><span>fallback</span></div>
  </div>

  <main class="container">
    <div class="controls">
      <input id="search" type="search" placeholder="Search questions, tools, or answers…" aria-label="Search evaluation cases">
      <select id="category" aria-label="Filter by category">
        <option value="">All categories</option>
        {category_options}
      </select>
    </div>
    <p id="visible-count">{summary["total"]} of {summary["total"]} cases shown</p>
    <section id="cases" aria-label="Evaluation cases">
      {cards}
    </section>
  </main>

  <footer class="container">Generated from evaluation/results-gpt-5.5.json</footer>

  <script>
    const search = document.querySelector("#search");
    const category = document.querySelector("#category");
    const cards = [...document.querySelectorAll(".case-card")];
    const count = document.querySelector("#visible-count");

    function filterCases() {{
      const query = search.value.trim().toLowerCase();
      const selectedCategory = category.value;
      let visible = 0;

      for (const card of cards) {{
        const matchesSearch = !query || card.dataset.search.includes(query);
        const matchesCategory = !selectedCategory || card.dataset.category === selectedCategory;
        card.hidden = !(matchesSearch && matchesCategory);
        if (!card.hidden) visible += 1;
      }}

      count.textContent = `${{visible}} of ${{cards.length}} cases shown`;
    }}

    search.addEventListener("input", filterCases);
    category.addEventListener("change", filterCases);
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=Path(__file__).with_name("results-gpt-5.5.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("results-gpt-5.5.html"),
    )
    args = parser.parse_args()

    report = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.write_text(render_report(report), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
