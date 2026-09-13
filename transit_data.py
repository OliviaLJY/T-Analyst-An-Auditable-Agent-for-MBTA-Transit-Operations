"""Deterministic MBTA data access and transit performance metrics."""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import requests

MBTA_API = "https://api-v3.mbta.com"
LAMP_INDEX = (
    "https://performancedata.mbta.com/lamp/"
    "subway-on-time-performance-v1/index.csv"
)
SUBWAY_ROUTES = ("Red", "Orange", "Blue", "Green-B", "Green-C", "Green-D", "Green-E")
LINE_GROUPS = {
    "Red": ("Red",),
    "Orange": ("Orange",),
    "Blue": ("Blue",),
    "Green": ("Green-B", "Green-C", "Green-D", "Green-E"),
}
METRIC_DEFINITIONS = {
    "headway_ratio": "Observed departure headway divided by scheduled headway.",
    "gap_rate": "Share of observed headways greater than 1.5× the scheduled headway.",
    "bunching_rate": "Share of observed headways below 0.5× the scheduled headway.",
    "travel_time_excess": "Observed inter-station travel time minus scheduled travel time.",
    "prediction_gap": (
        "Minutes between consecutive future predictions at one stop and direction. "
        "This is not a realized headway."
    ),
}


class TransitDataError(RuntimeError):
    """Raised when a public transit source cannot be loaded."""


def _get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    headers = {}
    if os.getenv("MBTA_API_KEY"):
        headers["x-api-key"] = os.environ["MBTA_API_KEY"]
    try:
        response = requests.get(
            f"{MBTA_API}/{path}", params=params, headers=headers, timeout=20
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise TransitDataError(f"MBTA request failed: {exc}") from exc


def _relationship_id(resource: dict[str, Any], name: str) -> str | None:
    data = resource.get("relationships", {}).get(name, {}).get("data")
    if isinstance(data, dict):
        return data.get("id")
    return None


def fetch_live_snapshot() -> dict[str, Any]:
    """Fetch one internally consistent-enough snapshot for the dashboard."""
    route_filter = ",".join(SUBWAY_ROUTES)
    fetched_at = datetime.now(timezone.utc).isoformat()
    vehicles_raw = _get("vehicles", {"filter[route]": route_filter})
    alerts_raw = _get("alerts", {"filter[route]": route_filter})
    predictions_raw = _get(
        "predictions",
        {"filter[route]": route_filter, "include": "stop"},
    )

    included_stops = {
        item["id"]: item.get("attributes", {}).get("name", item["id"])
        for item in predictions_raw.get("included", [])
        if item.get("type") == "stop"
    }
    vehicles = []
    for item in vehicles_raw.get("data", []):
        attrs = item.get("attributes", {})
        vehicles.append(
            {
                "vehicle_id": item.get("id"),
                "route_id": _relationship_id(item, "route"),
                "latitude": attrs.get("latitude"),
                "longitude": attrs.get("longitude"),
                "bearing": attrs.get("bearing"),
                "status": attrs.get("current_status"),
                "updated_at": attrs.get("updated_at"),
            }
        )

    alerts = []
    for item in alerts_raw.get("data", []):
        attrs = item.get("attributes", {})
        entities = attrs.get("informed_entity") or []
        routes = sorted(
            {
                entity.get("route")
                for entity in entities
                if entity.get("route") in SUBWAY_ROUTES
            }
        )
        alerts.append(
            {
                "alert_id": item.get("id"),
                "effect": attrs.get("effect"),
                "header": attrs.get("header"),
                "routes": routes,
                "updated_at": attrs.get("updated_at"),
            }
        )

    predictions = []
    now = datetime.now(timezone.utc)
    for item in predictions_raw.get("data", []):
        attrs = item.get("attributes", {})
        timestamp = attrs.get("departure_time") or attrs.get("arrival_time")
        if not timestamp:
            continue
        try:
            event_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            continue
        if event_time < now:
            continue
        stop_id = _relationship_id(item, "stop")
        predictions.append(
            {
                "route_id": _relationship_id(item, "route"),
                "stop_id": stop_id,
                "stop_name": included_stops.get(stop_id, stop_id),
                "direction_id": attrs.get("direction_id"),
                "event_time": event_time.isoformat(),
                "minutes_away": round((event_time - now).total_seconds() / 60, 1),
                "status": attrs.get("status"),
            }
        )
    return {
        "fetched_at": fetched_at,
        "vehicles": vehicles,
        "alerts": alerts,
        "predictions": predictions,
    }


def live_line_status(snapshot: dict[str, Any], line: str | None = None) -> dict[str, Any]:
    """Summarize alerts, vehicles, and the largest upcoming prediction gaps."""
    selected = LINE_GROUPS.get(line or "", SUBWAY_ROUTES)
    vehicles = [v for v in snapshot["vehicles"] if v["route_id"] in selected]
    alerts = [
        alert
        for alert in snapshot["alerts"]
        if not alert["routes"] or set(alert["routes"]).intersection(selected)
    ]
    predictions = pd.DataFrame(snapshot["predictions"])
    largest_gaps: list[dict[str, Any]] = []
    if not predictions.empty:
        predictions = predictions[predictions["route_id"].isin(selected)].copy()
        predictions["event_time"] = pd.to_datetime(predictions["event_time"], utc=True)
        predictions = predictions.sort_values("event_time")
        predictions["gap_minutes"] = (
            predictions.groupby(["route_id", "stop_id", "direction_id"], dropna=False)[
                "event_time"
            ]
            .diff()
            .dt.total_seconds()
            .div(60)
        )
        gap_rows = predictions.nlargest(5, "gap_minutes")
        largest_gaps = gap_rows[
            ["route_id", "stop_name", "direction_id", "gap_minutes"]
        ].round({"gap_minutes": 1}).to_dict("records")
    return {
        "line": line or "Network",
        "as_of": snapshot["fetched_at"],
        "vehicle_count": len(vehicles),
        "active_alert_count": len(alerts),
        "alerts": alerts[:8],
        "largest_prediction_gaps": largest_gaps,
        "caveat": METRIC_DEFINITIONS["prediction_gap"],
    }


def prepare_history(cache_dir: str | Path = "data/cache", days: int = 7) -> list[Path]:
    """Download the most recent complete LAMP service days, using a local cache."""
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    try:
        index = pd.read_csv(LAMP_INDEX)
    except Exception as exc:
        cached = sorted(cache.glob("*-subway-on-time-performance-v1.parquet"))
        if cached:
            return cached[-days:]
        raise TransitDataError(f"LAMP index download failed: {exc}") from exc
    index["service_date"] = pd.to_datetime(index["service_date"]).dt.date
    latest_complete = date.today() - timedelta(days=1)
    chosen = index[index["service_date"] <= latest_complete].tail(days)
    paths = []
    for row in chosen.itertuples(index=False):
        destination = cache / Path(row.file_url).name
        if not destination.exists() or destination.stat().st_size == 0:
            try:
                response = requests.get(row.file_url, timeout=60)
                response.raise_for_status()
                destination.write_bytes(response.content)
            except requests.RequestException as exc:
                raise TransitDataError(f"LAMP file download failed: {exc}") from exc
        paths.append(destination)
    if not paths:
        raise TransitDataError("No complete LAMP service dates were available.")
    return paths


def load_history(paths: Iterable[str | Path]) -> pd.DataFrame:
    frames = [pd.read_parquet(path) for path in paths]
    if not frames:
        raise TransitDataError("No historical files were supplied.")
    return pd.concat(frames, ignore_index=True)


def _metric_frame(history: pd.DataFrame) -> pd.DataFrame:
    data = history.copy()
    required = {
        "route_id",
        "headway_branch_seconds",
        "scheduled_headway_branch",
        "travel_time_seconds",
        "scheduled_travel_time",
    }
    missing = required.difference(data.columns)
    if missing:
        raise TransitDataError(f"LAMP schema is missing: {sorted(missing)}")
    observed = pd.to_numeric(data["headway_branch_seconds"], errors="coerce")
    scheduled = pd.to_numeric(data["scheduled_headway_branch"], errors="coerce")
    if "headway_trunk_seconds" in data:
        observed = observed.fillna(pd.to_numeric(data["headway_trunk_seconds"], errors="coerce"))
    if "scheduled_headway_trunk" in data:
        scheduled = scheduled.fillna(pd.to_numeric(data["scheduled_headway_trunk"], errors="coerce"))
    data["observed_headway"] = observed
    data["scheduled_headway"] = scheduled
    valid = scheduled.gt(0) & observed.gt(0)
    data["headway_ratio"] = (observed / scheduled).where(valid)
    data["gap"] = data["headway_ratio"].gt(1.5).where(valid)
    data["bunched"] = data["headway_ratio"].lt(0.5).where(valid)
    data["travel_time_excess"] = (
        pd.to_numeric(data["travel_time_seconds"], errors="coerce")
        - pd.to_numeric(data["scheduled_travel_time"], errors="coerce")
    )
    return data


def network_reliability(
    history: pd.DataFrame, line: str | None = None
) -> list[dict[str, Any]]:
    """Aggregate interpretable reliability metrics by route."""
    data = _metric_frame(history)
    data = data[data["route_id"].isin(SUBWAY_ROUTES)]
    if line:
        data = data[data["route_id"].isin(LINE_GROUPS.get(line, (line,)))]
    summary = (
        data.groupby("route_id", dropna=False)
        .agg(
            observations=("headway_ratio", "count"),
            median_headway_ratio=("headway_ratio", "median"),
            p90_headway_ratio=("headway_ratio", lambda value: value.quantile(0.9)),
            gap_rate=("gap", "mean"),
            bunching_rate=("bunched", "mean"),
            median_travel_time_excess_seconds=("travel_time_excess", "median"),
        )
        .reset_index()
        .sort_values("gap_rate", ascending=False)
    )
    for column in (
        "median_headway_ratio",
        "p90_headway_ratio",
        "gap_rate",
        "bunching_rate",
        "median_travel_time_excess_seconds",
    ):
        summary[column] = pd.to_numeric(summary[column], errors="coerce").round(3)
    return json.loads(summary.to_json(orient="records"))


def station_headways(
    history: pd.DataFrame, station: str, line: str | None = None
) -> dict[str, Any]:
    """Summarize headways at a stop ID or a case-insensitive stop-name match."""
    data = _metric_frame(history)
    data = data[data["route_id"].isin(SUBWAY_ROUTES)]
    if line:
        data = data[data["route_id"].isin(LINE_GROUPS.get(line, (line,)))]
    stop_column = "parent_station" if "parent_station" in data.columns else "stop_id"
    mask = data[stop_column].astype(str).str.contains(station, case=False, regex=False)
    selected = data[mask]
    if selected.empty:
        return {"station": station, "error": "No matching station in the selected data."}
    return {
        "station": station,
        "matched_values": sorted(selected[stop_column].dropna().astype(str).unique())[:10],
        "observations": int(selected["headway_ratio"].count()),
        "median_headway_minutes": round(selected["observed_headway"].median() / 60, 2),
        "p90_headway_minutes": round(selected["observed_headway"].quantile(0.9) / 60, 2),
        "gap_rate": round(float(selected["gap"].mean()), 3),
        "bunching_rate": round(float(selected["bunched"].mean()), 3),
    }


def metric_definition(metric: str | None = None) -> dict[str, str]:
    if metric:
        return {metric: METRIC_DEFINITIONS.get(metric, "Unknown metric.")}
    return METRIC_DEFINITIONS
