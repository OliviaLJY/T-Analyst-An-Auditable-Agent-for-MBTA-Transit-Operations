# AI Use

I used AI in two places: during development, and inside the final app.

## Development

I used Cursor's coding agent throughout the project to speed up implementation,
debugging, and iteration.

I chose the Agentic AI track, MBTA as the target agency, and the overall idea of
building an auditable transit-operations agent. Cursor then helped me implement
and refine the project.

In particular, I used it to:

- look through the MBTA V3 API, LAMP, and Parley documentation;
- implement early versions of the data loader, transit metrics, agent workflow,
  Streamlit UI, and tests;
- debug a pandas dtype issue that appeared when I ran the code on real LAMP files;
- revise the UI after testing the first version;
- build the fixed-question agent evaluation;
- help edit the repository documentation.

I tested the generated code on seven real LAMP service-day files and a live MBTA
API snapshot rather than relying only on code inspection. I also checked the
Parley model endpoint and confirmed that `gpt-5.5` was available.

## AI inside the app

The app uses MIT Parley GPT-5.5 twice for a normal question.

The first call turns the user's question into a small JSON tool plan. Python then
runs the selected tools. The second call turns the returned evidence into a
readable answer.

GPT-5.5 does not calculate the transit metrics itself and cannot run arbitrary
SQL. Tool names and arguments are validated before execution, and the final
answer must cite evidence IDs created during the same request. If citation
validation fails, the app returns a deterministic summary instead.

## Guardrails

API keys are loaded from environment variables and are not committed to the
repository.

The app sends the user's question and compact public MBTA evidence to Parley. It
does not send private transit data, unpublished research, or personally
identifiable information.