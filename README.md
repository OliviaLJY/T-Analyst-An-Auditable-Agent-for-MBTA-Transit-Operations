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

The repository includes a fixed set of 15 questions covering network and line
reliability, station headways, live status, metric definitions, a multi-tool
comparison, and two Chinese questions. The evaluation checks three behaviors:

- whether the planner selected the expected tool and required arguments;
- whether the final answer cites only evidence IDs from the same run;
- whether deterministic fallback behavior was triggered.

Run the GPT-5.5 evaluation from a shell with the Parley key:

```bash
python evaluate_agent.py
```

This makes 15 planning calls and 15 answer calls, then writes CSV, JSON, and
Markdown results under `evaluation/`. To evaluate no-key behavior instead:

```bash
python evaluate_agent.py --force-fallback
```

The committed [fallback baseline](evaluation/results-fallback.md) selects the
expected tools for 15/15 questions and returns valid final citations for 15/15.
All 15 rows correctly report that fallback was used. The fallback run therefore
has zero full-agent passes, because a full pass requires correct tools, valid
citations, and no fallback.

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
