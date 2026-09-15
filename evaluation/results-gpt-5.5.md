# Agent Evaluation — Parley GPT-5.5

- Run time: `2026-09-15T03:25:50.405701+00:00`
- Model: `gpt-5.5`
- Questions: 20
- Correct tool selection: 20/20 (100.0%)
- Valid final citations: 20/20 (100.0%)
- Usable tool results: 20/20 (100.0%)
- Fallbacks triggered: 0/20
- End-to-end pass: 20/20 (correct tools + usable results + valid citations + no fallback)

| ID | Category | Expected tools | Selected tools | Tool | Result | Citation | Fallback | Pass |
|---|---|---|---|---:|---:|---:|---:|---:|
| hist-network-ranking | historical network | network_reliability | network_reliability | Yes | Yes | Yes | No | Yes |
| hist-red | historical line | network_reliability | network_reliability | Yes | Yes | Yes | No | Yes |
| hist-green | historical line | network_reliability | network_reliability | Yes | Yes | Yes | No | Yes |
| hist-blue | historical line | network_reliability | network_reliability | Yes | Yes | Yes | No | Yes |
| live-orange | live line | live_line_status | live_line_status | Yes | Yes | Yes | No | Yes |
| live-blue | live line | live_line_status | live_line_status | Yes | Yes | Yes | No | Yes |
| live-network | live network | live_line_status | live_line_status | Yes | Yes | Yes | No | Yes |
| station-harvard | historical station | station_headways | station_headways | Yes | Yes | Yes | No | Yes |
| station-kendall | historical station | station_headways | station_headways | Yes | Yes | Yes | No | Yes |
| station-state | historical station | station_headways | station_headways | Yes | Yes | Yes | No | Yes |
| define-gap | methodology | metric_definition | metric_definition | Yes | Yes | Yes | No | Yes |
| define-prediction | methodology | metric_definition | metric_definition | Yes | Yes | Yes | No | Yes |
| compare-orange | multi-tool | live_line_status<br>network_reliability | live_line_status<br>network_reliability | Yes | Yes | Yes | No | Yes |
| live-red-notices | live line | live_line_status | live_line_status | Yes | Yes | Yes | No | Yes |
| define-two-metrics | methodology | metric_definition | metric_definition | Yes | Yes | Yes | No | Yes |
| station-harvard-square | station alias | station_headways | station_headways | Yes | Yes | Yes | No | Yes |
| station-kendall-square | station alias | station_headways | station_headways | Yes | Yes | Yes | No | Yes |
| station-mit | station alias | station_headways | station_headways | Yes | Yes | Yes | No | Yes |
| station-state-street | station alias | station_headways | station_headways | Yes | Yes | Yes | No | Yes |
| station-park-street | dynamic station index | station_headways | station_headways | Yes | Yes | Yes | No | Yes |

Tool-call order is ignored. Expected arguments must appear in the selected call; the planner may add an optional supported argument.

A fallback is recorded when no API key is used or when the model answer fails citation validation.
