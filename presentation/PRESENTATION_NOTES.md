# T-Analyst Presentation Notes

These notes are written for a 6–8 minute presentation, followed by a short live
demo.

## Slide 1 — T-Analyst

I built T-Analyst to explore one question: can an AI agent make transit
operations data easier to use without making the analysis harder to trust?

The app combines live MBTA information, completed operations data, and a
natural-language interface. The main design choice is that every numerical
answer remains connected to visible evidence.

## Slide 2 — The problem

The MBTA publishes useful data, but a seemingly simple question still requires
quite a bit of work. Live feeds and historical performance files have different
structures and answer different questions. Transit terms also matter: for
example, a future prediction gap should not be presented as a realized
headway.

The third problem is trust. A chatbot can produce a confident answer, but the
answer is not useful for operations analysis if the user cannot inspect how the
number was produced.

## Slide 3 — The product

I designed the interface with two levels of detail. The Overview page gives a
quick view of vehicle locations, current notices, and recent train spacing.
The question page lets someone ask about service without knowing GTFS or SQL.

The first thing the user sees is a readable answer. The tool calls and returned
data are still available, but they are placed in an expandable panel so they do
not overwhelm someone who only wants the result.

## Slide 4 — The data

The live side uses three MBTA V3 endpoints: vehicles, alerts, and predictions.
These tell me what the feeds are reporting now.

The historical side uses MBTA LAMP daily subway performance files. They contain
completed trip-stop observations and matched schedule fields, which makes it
possible to compare realized and planned headways.

For the submitted snapshot, I used the latest seven complete service days:
September 6 through September 12. This produced 298,851 trip-stop rows. I
exclude the current day because its file may still be accumulating.

## Slide 5 — Agent design

The language model has a deliberately narrow role. GPT-5.5 converts a question
into a JSON plan. Pydantic checks the tool name, required arguments, and route
values. Regular Python then executes the selected read-only tools.

The results are packaged as evidence with IDs. GPT-5.5 receives that evidence
and writes the final explanation. The model never calculates the displayed
metric and cannot generate arbitrary SQL.

## Slide 6 — Auditability

This is the path for a typical question. “How has the Red Line been running?”
becomes a validated call to the network reliability tool with `line=Red`.

The tool returns LAMP-based metrics as evidence E1. The answer can then state
that 9.3% of usable intervals were unusually long, but it must cite E1. If the
model returns an unsupported citation—or no evidence citation—the application
replaces it with a deterministic summary.

## Slide 7 — Example finding

In this seven-day window, all four Green Line branches had a larger share of
unusually long intervals than Red, Blue, or Orange. Green-D was highest at
17.5%, based on 38,840 usable headway observations.

I would not describe that as a long-term ranking. The Green Line has branches
and shared downtown infrastructure, and this small comparison does not control
for day type, time of day, incidents, or construction. I treat the result as a
useful lead for the next analysis.

## Slide 8 — Why it stands out

The project is more than a dashboard because it can answer a new question and
show its reasoning path. It is more constrained than a general transit chatbot
because the model can only use four validated tools.

It also reflects transit data semantics. Realized headways and prediction gaps
remain separate, and the historical schedule comparisons come from matched
LAMP fields. Finally, the data preparation, tests, and chart generation are
reproducible.

## Slide 9 — Limits and next steps

The largest limitation is the short historical window. Seven days are enough
for a demonstration, not a service baseline. I also do not separate peak and
off-peak service or weekdays and weekends.

My first extension would be a Green Line branch-versus-trunk analysis by time
of day. On the agent side, I would add data-quality confidence to each evidence
package and evaluate tool selection and answer grounding across a larger set of
questions.

## Slide 10 — Close and demo

The idea I want to leave with is that a useful agent does not have to answer
everything. It should be clear about what it can answer and show why those
answers should be trusted.

For the live demo, ask: “How has the Red Line been running?” First show the
answer, then open “See how this answer was made” and point out the interpreted
question, validated tool call, source, and E1 evidence.
