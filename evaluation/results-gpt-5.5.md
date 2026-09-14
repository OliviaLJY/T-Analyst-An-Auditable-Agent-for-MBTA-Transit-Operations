# Agent Evaluation — Parley GPT-5.5

- Run time: `2026-09-14T15:24:58.012345+00:00`
- Model: `gpt-5.5`
- Questions: 15
- Correct tool selection: 15/15 (100.0%)
- Valid final citations: 15/15 (100.0%)
- Fallbacks triggered: 0/15
- End-to-end pass: 15/15 (correct tools + valid citations + no fallback)

| ID | Category | Expected tools | Selected tools | Tool | Citation | Fallback | Pass |
|---|---|---|---|---:|---:|---:|---:|
| hist-network-ranking | historical network | network_reliability | network_reliability | Yes | Yes | No | Yes |
| hist-red | historical line | network_reliability | network_reliability | Yes | Yes | No | Yes |
| hist-green | historical line | network_reliability | network_reliability | Yes | Yes | No | Yes |
| hist-blue | historical line | network_reliability | network_reliability | Yes | Yes | No | Yes |
| live-orange | live line | live_line_status | live_line_status | Yes | Yes | No | Yes |
| live-blue | live line | live_line_status | live_line_status | Yes | Yes | No | Yes |
| live-network | live network | live_line_status | live_line_status | Yes | Yes | No | Yes |
| station-harvard | historical station | station_headways | station_headways | Yes | Yes | No | Yes |
| station-kendall | historical station | station_headways | station_headways | Yes | Yes | No | Yes |
| station-state | historical station | station_headways | station_headways | Yes | Yes | No | Yes |
| define-gap | methodology | metric_definition | metric_definition | Yes | Yes | No | Yes |
| define-prediction | methodology | metric_definition | metric_definition | Yes | Yes | No | Yes |
| compare-orange | multi-tool | live_line_status<br>network_reliability | live_line_status<br>network_reliability | Yes | Yes | No | Yes |
| live-red-notices | live line | live_line_status | live_line_status | Yes | Yes | No | Yes |
| define-two-metrics | methodology | metric_definition | metric_definition | Yes | Yes | No | Yes |

Tool-call order is ignored. Expected arguments must appear in the selected call; the planner may add an optional supported argument.

A fallback is recorded when no API key is used or when the model answer fails citation validation.
