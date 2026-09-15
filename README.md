# T-Analyst: An Auditable Agent for MBTA Transit Operations

**Position/Track: Agentic AI**

I built T-Analyst for someone who has a question about subway service but does
not know how to work with GTFS, LAMP, or the MBTA APIs. The app puts a live
network view and a natural-language analysis tool in one place. More
importantly, it keeps the evidence visible: each answer can be traced back to
the tool call, parameters, source, timestamp, and rows used to produce it.

## Why this is useful

Transit data is public, but it is not especially approachable. Answering a
simple question such as “Which line had the most uneven spacing this week?”
usually means finding the right feed, understanding service dates, matching
observed and scheduled headways, and deciding what to do with missing values.

A chat interface lowers that barrier, but only if its answers can be checked.
For that reason, I did not let the language model calculate metrics or generate
arbitrary SQL. Its job is narrower: understand the question, choose from four
read-only tools, and explain the evidence those tools return. The calculations
remain regular Python code.

I limited the project to MBTA subway service. The historical view uses the
latest seven complete LAMP service days, while the live view uses a current
MBTA V3 API snapshot. This was enough scope to demonstrate an agentic workflow
without implying that a short prototype is a production operations system.

## Artifact

The Streamlit app has three main views:

1. **Overview** maps vehicles that are currently reporting a position, shows
   service notices, and compares recently realized train spacing by route.
2. **Ask a question** accepts everyday language and returns an answer with an
   optional “how this answer was made” panel.
3. **About the data** explains the workflow, metric definitions, and limits of
   the analysis.

Questions the artifact is designed to answer include:

- Which line had the most uneven train spacing recently?
- How has the Red Line been running?
- What is happening on the Orange Line right now?
- How does the app decide that a gap is unusually long?

A short project deck and speaking notes are available in
[presentation/](presentation/).

## Method

The historical data has one row for each observed trip-stop pair. For every row
with a usable observed and scheduled headway, I calculate:

- `headway ratio = observed headway / scheduled headway`
- `gap = headway ratio > 1.5`
- `bunched = headway ratio < 0.5`
- `travel-time excess = observed travel time - scheduled travel time`

A live prediction gap is the interval between consecutive future predictions
for one route, stop, and direction. I keep it separate from historical
headways: a prediction can change and is not proof of an actual passenger wait.

LAMP's exported `parent_station` values are MBTA place IDs rather than
rider-facing names. Before a station query runs, the app resolves common aliases
such as Harvard Square, Kendall, Kendall/MIT, Kendall Square, MIT, State, and
State Street to canonical IDs. For other subway stations, it uses the MBTA V3
stop index and a conservative fuzzy match. The evidence records the requested
name, canonical name, place ID, and resolution method.

When a user asks a question, Parley GPT-5.5 first returns a small JSON plan with
one to three tool calls. Pydantic checks the tool names, arguments, route names,
and required fields before anything runs. The selected Python tools then return
structured evidence with IDs such as `[E1]`. GPT-5.5 writes the final
explanation from that evidence. If the answer fails to cite evidence from the
same run, the app falls back to a deterministic summary rather than showing an
unsupported response.

## Key findings

The reproducible snapshot for September 6–12, 2026 contains 298,851 trip-stop
rows. In this window, the Green Line branches had the highest shares of
headways longer than 1.5 times their matched schedules. Green-D was highest at
17.5% across 38,840 usable headway observations. Green-B was close behind at
17.4%, followed by Green-E at 16.9% and Green-C at 14.2%. Red, Blue, and Orange
were lower at 9.3%, 7.2%, and 6.3%, respectively.

![Long-gap share by route](artifacts/recent_gap_rate.svg)

I would treat this as a lead for further analysis, not evidence that Green-D is
chronically the least reliable route. The Green Line branches share downtown
infrastructure, and this comparison does not control for weekday versus weekend
service, incidents, construction, or demand. My next step would be to separate
the results by day type and time of day, then compare branch headways with
headways on the shared trunk.

## Run locally

The submitted version was tested with Python 3.9.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Open .env and add the Parley key. .env is ignored by Git.
python check_parley.py
python prepare_data.py
streamlit run app.py
```

The app uses `https://parley.api.mit.edu/v1` and confirms `gpt-5.5` through the
API's `/v1/models` endpoint. An MBTA key is optional; anonymous requests are
enough for this prototype. Without a Parley key, the data views still work and
questions receive a simpler deterministic response.

Run tests with:

```bash
pytest -q
```

## Agent evaluation

T-Analyst includes a fixed 20-question evaluation suite covering historical
reliability, live service status, station-level headways, metric definitions,
station aliases, and multi-tool comparison.

The final GPT-5.5 evaluation achieved:

- correct tool selection: **20/20**
- usable tool results: **20/20**
- valid final citations: **20/20**
- fallbacks triggered: **0/20**
- end-to-end pass: **20/20**

The suite also includes station-alias and dynamic station-resolution cases such
as Harvard Square, Kendall Square, MIT, State Street, and Park Street.

This is a small development evaluation rather than a held-out benchmark. It is
used primarily as a repeatable regression check for tool selection, evidence
quality, entity resolution, and grounding.

Run:

```bash
python evaluate_agent.py

See the interactive evaluation report:
[evaluation report](evaluation/results-gpt-5.5.html)

## Data and resources

- [MBTA V3 API](https://www.mbta.com/developers/v3-api): live vehicles,
  predictions, and service alerts.
- [MBTA LAMP Public Data](https://performancedata.mbta.com/): daily subway
  performance Parquet files.
- [LAMP Data Dictionary](https://github.com/mbta/lamp/blob/main/Data_Dictionary.md):
  field definitions and calculated metrics.
- [MBTA GTFS documentation](https://github.com/mbta/gtfs-documentation):
  schedule and GTFS-Realtime implementation details.
- [MassDOT Developers License Agreement](https://www.mbta.com/developers):
  terms governing MBTA data use.
- Streamlit, pandas, Plotly, requests, OpenAI's Python client, and Pydantic are
  used under their respective open-source licenses.

I reviewed the task's references to TransitGPT and the Jarvus GTFS-RT Sandbox
while deciding on scope, but did not copy code from either project.

## Compute

- Platform: MIT Parley API through its OpenAI-compatible endpoint
- Model: `gpt-5.5`
- Access tier: MIT individual complimentary API credits ($30 per month)
- Local compute: Apple M4, 10 CPU cores, 16 GB memory

## Limitations

- Seven recent complete service days are insufficient for trend inference.
- The analysis does not control for incidents, construction, demand, or
  schedule changes.
- Missing or unmatched GTFS/GTFS-RT observations are excluded from the relevant
  metric.
- Real-time feeds are snapshots and may update immediately after display.
- Prediction gaps are not realized headways or guaranteed passenger waits.
- The tool registry supports a deliberately bounded set of question types.

Hours spent: 7
