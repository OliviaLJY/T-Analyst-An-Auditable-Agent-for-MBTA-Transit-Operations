# AI Use

I used AI in two different ways: as a coding assistant while building the
project, and as the language model inside the finished app.

## Development

I used Cursor's coding agent as an implementation and iteration tool throughout the project. I first reviewed the evaluation prompt and defined the project scope myself: I chose the Agentic AI track, selected MBTA as the target agency, and decided to build an auditable transit operations analyst. I also made the core design decisions, including the project name, the Streamlit-based interface, and the use of GPT-5.5 through MIT Parley.

After establishing the direction and system design, I used Cursor to help implement individual components, debug issues, and iterate more quickly within the time limit. I remained responsible for deciding what functionality to include, how the agent should behave, and which outputs were useful for a transit operations use case.

The coding agent helped with:

- researching the MBTA V3 API, LAMP exports, and Parley API format;
- proposing the planner → tool → evidence → answer architecture;
- writing the first versions of the data loader, metric functions, agent
  orchestration, Streamlit interface, and tests;
- diagnosing a pandas dtype issue that appeared on the real LAMP files;
- revising the interface after I asked for a clearer and more natural user
  experience;
- setting up a fixed-question evaluation for tool selection, evidence
  citations, and fallback behavior;
- drafting and editing the repository documentation.

I reviewed the running app between iterations and directed changes to the
scope, model, project name, and interface. AI-generated code was not accepted
only on appearance: the final version was run against seven actual LAMP files
and a live MBTA API snapshot. I also ran Parley's model check and confirmed
that the account exposes `gpt-5.5`.

## AI inside the app

The application uses MIT Parley GPT-5.5 twice for each successful question.
The first call converts the user's question into a small JSON plan. After
Python executes the selected tools, the second call turns the returned evidence
into a readable answer.

GPT-5.5 does not calculate the displayed transit metrics and cannot execute
arbitrary SQL. The allowed tools and parameters are validated before execution.
The final answer must cite evidence IDs generated during the same request. If
that check fails, the app shows a deterministic summary instead.

## Guardrails

The repository reads keys from environment variables. I checked that the Parley
key was not present in the files selected for submission. The app sends the
user's question and compact public MBTA evidence to Parley; it does not send
private transit data, unpublished research, or personally identifiable
information.
