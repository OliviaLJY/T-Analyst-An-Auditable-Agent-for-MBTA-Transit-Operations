"""Prepare, validate, and summarize the local MBTA historical cache."""

import json
from pathlib import Path

from transit_data import load_history, network_reliability, prepare_history


def write_artifacts(summary: list[dict], service_dates: list[str]) -> None:
    output = Path("artifacts")
    output.mkdir(exist_ok=True)
    payload = {"service_dates": service_dates, "routes": summary}
    (output / "recent_summary.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    width, height = 900, 470
    left, top, chart_width = 180, 75, 640
    bar_height, gap = 34, 15
    max_rate = max(float(row["gap_rate"]) for row in summary) or 1
    colors = {
        "Red": "#DA291C",
        "Orange": "#ED8B00",
        "Blue": "#003DA5",
        "Green-B": "#00843D",
        "Green-C": "#00843D",
        "Green-D": "#00843D",
        "Green-E": "#00843D",
    }
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="30" y="35" font-family="sans-serif" font-size="24" '
        'font-weight="bold">Share of realized headways classified as long gaps</text>',
        f'<text x="30" y="58" font-family="sans-serif" font-size="14" fill="#555">'
        f'MBTA LAMP service dates {service_dates[0]}–{service_dates[-1]} · '
        'gap = observed headway &gt; 1.5× scheduled</text>',
    ]
    for index, row in enumerate(summary):
        y = top + index * (bar_height + gap)
        rate = float(row["gap_rate"])
        bar_width = chart_width * rate / max_rate
        label = row["route_id"]
        lines.extend(
            [
                f'<text x="{left - 12}" y="{y + 23}" text-anchor="end" '
                f'font-family="sans-serif" font-size="16">{label}</text>',
                f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" '
                f'height="{bar_height}" rx="3" fill="{colors.get(label, "#555")}"/>',
                f'<text x="{left + bar_width + 10:.1f}" y="{y + 23}" '
                f'font-family="sans-serif" font-size="15">{rate * 100:.1f}%</text>',
            ]
        )
    lines.append("</svg>")
    (output / "recent_gap_rate.svg").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    paths = prepare_history(days=7)
    history = load_history(paths)
    summary = network_reliability(history)
    service_dates = [
        f"{value[:4]}-{value[4:6]}-{value[6:8]}"
        for value in sorted(history["service_date"].dropna().astype(str).unique())
    ]
    write_artifacts(summary, service_dates)
    print(f"Prepared {len(paths)} service days and {len(history):,} trip-stop rows.")
    print(f"Routes with valid headway observations: {len(summary)}")
    print("Wrote artifacts/recent_summary.json and artifacts/recent_gap_rate.svg")


if __name__ == "__main__":
    main()
