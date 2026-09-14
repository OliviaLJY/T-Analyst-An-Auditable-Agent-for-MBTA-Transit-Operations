"""Run a small, repeatable tool-selection and grounding evaluation."""

from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transit_agent import TransitAnalyst
from transit_data import fetch_live_snapshot, load_history, prepare_history

ROOT = Path(__file__).resolve().parent
QUESTIONS_PATH = ROOT / "evaluation" / "questions.json"


def normalized(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().casefold()
    return value


def arguments_match(expected: dict[str, Any], selected: dict[str, Any]) -> bool:
    """Treat expected arguments as a required subset of selected arguments."""
    return all(
        key in selected and normalized(selected[key]) == normalized(value)
        for key, value in expected.items()
    )


def calls_match(
    expected: list[dict[str, Any]], selected: list[dict[str, Any]]
) -> bool:
    """Match calls without requiring the planner to preserve call order."""
    if len(expected) != len(selected):
        return False
    remaining = selected.copy()
    for expected_call in expected:
        match_index = next(
            (
                index
                for index, selected_call in enumerate(remaining)
                if selected_call["name"] == expected_call["name"]
                and arguments_match(
                    expected_call.get("arguments", {}),
                    selected_call.get("arguments", {}),
                )
            ),
            None,
        )
        if match_index is None:
            return False
        remaining.pop(match_index)
    return not remaining


def compact_calls(calls: list[dict[str, Any]]) -> str:
    return "; ".join(
        f"{call['name']}({json.dumps(call.get('arguments', {}), ensure_ascii=False)})"
        for call in calls
    )


def write_results(payload: dict[str, Any], stem: str) -> None:
    output_dir = ROOT / "evaluation"
    json_path = output_dir / f"{stem}.json"
    csv_path = output_dir / f"{stem}.csv"
    markdown_path = output_dir / f"{stem}.md"

    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    fieldnames = [
        "id",
        "category",
        "question",
        "expected_calls",
        "selected_calls",
        "tool_selection_correct",
        "citation_valid",
        "fallback_triggered",
        "fallback_reason",
        "passed",
        "error",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in payload["results"]:
            writer.writerow({key: row.get(key) for key in fieldnames})

    summary = payload["summary"]
    lines = [
        f"# Agent Evaluation — {payload['mode']}",
        "",
        f"- Run time: `{payload['run_at']}`",
        f"- Model: `{payload['model']}`",
        f"- Questions: {summary['total']}",
        (
            f"- Correct tool selection: {summary['tool_selection_correct']}/"
            f"{summary['total']} ({summary['tool_selection_rate']:.1%})"
        ),
        (
            f"- Valid final citations: {summary['citation_valid']}/"
            f"{summary['total']} ({summary['citation_valid_rate']:.1%})"
        ),
        f"- Fallbacks triggered: {summary['fallback_triggered']}/{summary['total']}",
        (
            f"- End-to-end pass: {summary['passed']}/{summary['total']} "
            "(correct tools + valid citations + no fallback)"
        ),
        "",
        "| ID | Category | Expected tools | Selected tools | Tool | Citation | Fallback | Pass |",
        "|---|---|---|---|---:|---:|---:|---:|",
    ]
    for row in payload["results"]:
        expected_tools = "<br>".join(
            call["name"] for call in row["expected_calls_raw"]
        )
        selected_tools = (
            "<br>".join(call["name"] for call in row["selected_calls_raw"])
            or row.get("error")
            or "—"
        )
        mark = lambda value: "Yes" if value else "No"
        lines.append(
            f"| {row['id']} | {row['category']} | {expected_tools} | "
            f"{selected_tools} | {mark(row['tool_selection_correct'])} | "
            f"{mark(row['citation_valid'])} | {mark(row['fallback_triggered'])} | "
            f"{mark(row['passed'])} |"
        )
    lines.extend(
        [
            "",
            "Tool-call order is ignored. Expected arguments must appear in the selected "
            "call; the planner may add an optional supported argument.",
            "",
            "A fallback is recorded when no API key is used or when the model answer "
            "fails citation validation.",
        ]
    )
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {json_path.relative_to(ROOT)}")
    print(f"Wrote {csv_path.relative_to(ROOT)}")
    print(f"Wrote {markdown_path.relative_to(ROOT)}")


def run(force_fallback: bool, limit: int | None) -> dict[str, Any]:
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    if limit:
        questions = questions[:limit]
    key = None if force_fallback else os.getenv("TRANSIT_LLM_API_KEY")
    if not force_fallback and not key:
        raise SystemExit(
            "TRANSIT_LLM_API_KEY is not available. Export it or use --force-fallback."
        )

    history = load_history(prepare_history(days=7))
    live = fetch_live_snapshot()
    analyst = TransitAnalyst(history, live, api_key=key)
    if force_fallback:
        analyst.api_key = None
        analyst.client = None

    results = []
    model = "deterministic-fallback"
    for index, case in enumerate(questions, start=1):
        print(f"[{index}/{len(questions)}] {case['id']}")
        selected_calls: list[dict[str, Any]] = []
        try:
            result = analyst.ask(case["question"])
            model = result.model
            selected_calls = [
                call.model_dump() for call in result.plan.calls
            ]
            tool_correct = calls_match(case["expected_calls"], selected_calls)
            citation_valid = result.citation_valid
            fallback_triggered = result.fallback_triggered
            fallback_reason = result.fallback_reason or ""
            error = ""
            answer = result.answer
        except Exception as exc:
            tool_correct = False
            citation_valid = False
            fallback_triggered = False
            fallback_reason = ""
            error = f"{type(exc).__name__}: {exc}"
            answer = ""
        passed = (
            tool_correct
            and citation_valid
            and not fallback_triggered
            and not error
        )
        results.append(
            {
                "id": case["id"],
                "category": case["category"],
                "question": case["question"],
                "expected_calls": compact_calls(case["expected_calls"]),
                "selected_calls": compact_calls(selected_calls),
                "expected_calls_raw": case["expected_calls"],
                "selected_calls_raw": selected_calls,
                "tool_selection_correct": tool_correct,
                "citation_valid": citation_valid,
                "fallback_triggered": fallback_triggered,
                "fallback_reason": fallback_reason,
                "passed": passed,
                "error": error,
                "answer": answer,
            }
        )

    total = len(results)
    count = lambda field: sum(bool(row[field]) for row in results)
    tool_count = count("tool_selection_correct")
    citation_count = count("citation_valid")
    payload = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "mode": "fallback baseline" if force_fallback else "Parley GPT-5.5",
        "model": model,
        "summary": {
            "total": total,
            "tool_selection_correct": tool_count,
            "tool_selection_rate": tool_count / total if total else 0,
            "citation_valid": citation_count,
            "citation_valid_rate": citation_count / total if total else 0,
            "fallback_triggered": count("fallback_triggered"),
            "passed": count("passed"),
            "errors": sum(bool(row["error"]) for row in results),
        },
        "results": results,
    }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force-fallback",
        action="store_true",
        help="Evaluate deterministic no-key behavior instead of Parley.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Run only the first N questions for a quick smoke test.",
    )
    args = parser.parse_args()
    payload = run(force_fallback=args.force_fallback, limit=args.limit)
    stem = (
        "results-fallback"
        if args.force_fallback
        else "results-gpt-5.5"
    )
    write_results(payload, stem)
    summary = payload["summary"]
    print(
        f"Tool selection {summary['tool_selection_correct']}/{summary['total']} · "
        f"citations {summary['citation_valid']}/{summary['total']} · "
        f"fallbacks {summary['fallback_triggered']}/{summary['total']} · "
        f"passes {summary['passed']}/{summary['total']}"
    )


if __name__ == "__main__":
    main()
