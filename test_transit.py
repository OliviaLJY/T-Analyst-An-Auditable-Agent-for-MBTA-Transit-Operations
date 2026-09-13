from datetime import datetime, timedelta, timezone

import pandas as pd

from transit_agent import TransitAnalyst
from transit_data import live_line_status, network_reliability, station_headways


def history_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "route_id": ["Red", "Red", "Orange", "Orange"],
            "parent_station": ["Harvard", "Harvard", "State", "State"],
            "headway_branch_seconds": [300, 900, 360, 180],
            "headway_trunk_seconds": [None, None, None, None],
            "scheduled_headway_branch": [600, 600, 360, 360],
            "scheduled_headway_trunk": [None, None, None, None],
            "travel_time_seconds": [180, 240, 200, 210],
            "scheduled_travel_time": [180, 180, 180, 180],
        }
    )


def live_fixture() -> dict:
    now = datetime.now(timezone.utc)
    return {
        "fetched_at": now.isoformat(),
        "vehicles": [{"route_id": "Red"}, {"route_id": "Orange"}],
        "alerts": [
            {
                "alert_id": "1",
                "effect": "DELAY",
                "header": "Red Line delays",
                "routes": ["Red"],
            }
        ],
        "predictions": [
            {
                "route_id": "Red",
                "stop_id": "place-harsq",
                "stop_name": "Harvard",
                "direction_id": 0,
                "event_time": (now + timedelta(minutes=2)).isoformat(),
                "minutes_away": 2,
                "status": None,
            },
            {
                "route_id": "Red",
                "stop_id": "place-harsq",
                "stop_name": "Harvard",
                "direction_id": 0,
                "event_time": (now + timedelta(minutes=12)).isoformat(),
                "minutes_away": 12,
                "status": None,
            },
        ],
    }


def test_network_metrics_are_deterministic() -> None:
    result = network_reliability(history_fixture())
    red = next(row for row in result if row["route_id"] == "Red")
    assert red["observations"] == 2
    assert red["median_headway_ratio"] == 1.0
    assert red["gap_rate"] == 0.0


def test_station_match_uses_parent_station_name() -> None:
    result = station_headways(history_fixture(), "harv", line="Red")
    assert result["matched_values"] == ["Harvard"]
    assert result["observations"] == 2
    assert result["median_headway_minutes"] == 10.0


def test_live_status_keeps_prediction_caveat() -> None:
    result = live_line_status(live_fixture(), "Red")
    assert result["vehicle_count"] == 1
    assert result["active_alert_count"] == 1
    assert result["largest_prediction_gaps"][0]["gap_minutes"] == 10.0
    assert "not a realized headway" in result["caveat"]


def test_agent_without_key_uses_auditable_fallback() -> None:
    analyst = TransitAnalyst(history_fixture(), live_fixture(), api_key=None)
    analyst.api_key = None
    analyst.client = None
    result = analyst.ask("What is happening on the Red Line now?")
    assert result.used_llm is False
    assert result.plan.calls[0].name == "live_line_status"
    assert "[E1]" in result.answer
