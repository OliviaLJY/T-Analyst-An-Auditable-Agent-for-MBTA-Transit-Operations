# Agent Evaluation — fallback baseline

- Run time: `2026-09-14T15:22:09.547272+00:00`
- Model: `deterministic-fallback`
- Questions: 15
- Correct tool selection: 15/15 (100.0%)
- Valid final citations: 15/15 (100.0%)
- Fallbacks triggered: 15/15
- End-to-end pass: 0/15 (correct tools + valid citations + no fallback)

| ID | Category | Expected tools | Selected tools | Tool | Citation | Fallback | Pass |
|---|---|---|---|---:|---:|---:|---:|
| hist-network-ranking | historical network | network_reliability | network_reliability | Yes | Yes | Yes | No |
| hist-red | historical line | network_reliability | network_reliability | Yes | Yes | Yes | No |
| hist-green | historical line | network_reliability | network_reliability | Yes | Yes | Yes | No |
| hist-blue | historical line | network_reliability | network_reliability | Yes | Yes | Yes | No |
| live-orange | live line | live_line_status | live_line_status | Yes | Yes | Yes | No |
| live-blue | live line | live_line_status | live_line_status | Yes | Yes | Yes | No |
| live-network | live network | live_line_status | live_line_status | Yes | Yes | Yes | No |
| station-harvard | historical station | station_headways | station_headways | Yes | Yes | Yes | No |
| station-kendall | historical station | station_headways | station_headways | Yes | Yes | Yes | No |
| station-state | historical station | station_headways | station_headways | Yes | Yes | Yes | No |
| define-gap | methodology | metric_definition | metric_definition | Yes | Yes | Yes | No |
| define-prediction | methodology | metric_definition | metric_definition | Yes | Yes | Yes | No |
| compare-orange | multi-tool | live_line_status<br>network_reliability | live_line_status<br>network_reliability | Yes | Yes | Yes | No |
| live-red-notices | live line | live_line_status | live_line_status | Yes | Yes | Yes | No |
| define-two-metrics | methodology | metric_definition | metric_definition | Yes | Yes | Yes | No |

Tool-call order is ignored. Expected arguments must appear in the selected call; the planner may add an optional supported argument.

A fallback is recorded when no API key is used or when the model answer fails citation validation.
