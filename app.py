"""T-Analyst: An Auditable Agent for MBTA Transit Operations."""

from __future__ import annotations

import html
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from transit_agent import TransitAnalyst
from transit_data import (
    LINE_GROUPS,
    TransitDataError,
    fetch_live_snapshot,
    live_line_status,
    load_history,
    metric_definition,
    network_reliability,
    prepare_history,
)

st.set_page_config(
    page_title="T-Analyst: An Auditable Agent for MBTA Transit Operations",
    page_icon="T",
    layout="wide",
    initial_sidebar_state="expanded",
)

LINE_COLORS = {
    "Red": "#DA291C",
    "Orange": "#ED8B00",
    "Blue": "#003DA5",
    "Green": "#00843D",
    "Green-B": "#00843D",
    "Green-C": "#00843D",
    "Green-D": "#00843D",
    "Green-E": "#00843D",
}

st.markdown(
    """
    <style>
    :root {
        --ink: #102a3a;
        --muted: #5f6f79;
        --line: #dfe7eb;
        --paper: #ffffff;
        --wash: #f4f7f8;
        --accent: #007a73;
    }
    .stApp { background: #f7f9fa; color: var(--ink); }
    .block-container {
        max-width: 1380px;
        padding-top: 1.6rem;
        padding-bottom: 4rem;
    }
    h1, h2, h3 { letter-spacing: -0.035em; color: var(--ink); }
    [data-testid="stSidebar"] {
        background: #eef3f4;
        border-right: 1px solid #d8e1e5;
    }
    [data-testid="stSidebar"] .block-container { padding-top: 2rem; }
    .hero {
        position: relative;
        overflow: hidden;
        padding: 2.2rem 2.4rem;
        margin-bottom: 1.2rem;
        border-radius: 20px;
        color: white;
        background:
          radial-gradient(circle at 88% 20%, rgba(72, 201, 176, .28), transparent 27%),
          linear-gradient(120deg, #071b28 0%, #123746 100%);
        box-shadow: 0 14px 36px rgba(13, 40, 54, .13);
    }
    .hero h1 {
        margin: .25rem 0 .35rem;
        color: white;
        font-size: clamp(2.2rem, 5vw, 4rem);
        line-height: 1;
    }
    .hero p { margin: 0; max-width: 700px; color: #d7e7ec; font-size: 1.08rem; }
    .eyebrow {
        font-size: .84rem;
        font-weight: 650;
        letter-spacing: .02em;
        color: #77d7c7;
    }
    .hero-badges { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1.25rem; }
    .badge {
        display: inline-flex;
        align-items: center;
        gap: .4rem;
        padding: .38rem .68rem;
        border: 1px solid rgba(255,255,255,.2);
        border-radius: 999px;
        background: rgba(255,255,255,.08);
        color: #eef8fa;
        font-size: .8rem;
    }
    .live-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #63e6be;
        box-shadow: 0 0 0 4px rgba(99,230,190,.13);
    }
    [data-testid="stMetric"] {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        box-shadow: 0 4px 14px rgba(26, 52, 65, .045);
    }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"] { color: var(--ink); font-weight: 720; }
    .line-card {
        min-height: 116px;
        padding: 1rem 1.05rem;
        border-radius: 14px;
        border: 1px solid var(--line);
        border-top: 5px solid var(--route-color);
        background: white;
        box-shadow: 0 4px 14px rgba(26, 52, 65, .045);
    }
    .line-name { font-size: 1.05rem; font-weight: 740; color: var(--ink); }
    .line-value { margin-top: .55rem; font-size: 1.5rem; font-weight: 760; color: var(--ink); }
    .line-meta { color: var(--muted); font-size: .8rem; }
    .section-kicker {
        color: var(--accent);
        font-size: .72rem;
        font-weight: 750;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-bottom: .15rem;
    }
    .section-copy { color: var(--muted); margin-top: -.35rem; margin-bottom: 1.1rem; }
    .insight {
        padding: 1rem 1.15rem;
        border-left: 4px solid var(--accent);
        border-radius: 4px 12px 12px 4px;
        background: #eaf5f3;
        color: #174840;
        margin: .45rem 0 1.2rem;
    }
    .alert-card {
        padding: .9rem 1rem;
        margin-bottom: .7rem;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: white;
    }
    .alert-effect {
        display: inline-block;
        margin-bottom: .4rem;
        padding: .18rem .45rem;
        border-radius: 5px;
        background: #fff1e8;
        color: #9d3e00;
        font-size: .68rem;
        font-weight: 780;
        letter-spacing: .06em;
    }
    .alert-title { font-size: .9rem; font-weight: 650; line-height: 1.35; }
    .alert-routes { margin-top: .35rem; color: var(--muted); font-size: .76rem; }
    .empty-state {
        padding: 2.2rem;
        border: 1px dashed #b8c8cf;
        border-radius: 14px;
        background: white;
        text-align: center;
        color: var(--muted);
    }
    .method-card {
        min-height: 155px;
        padding: 1.1rem;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: white;
    }
    .method-number { color: var(--accent); font-weight: 800; font-size: .75rem; }
    .method-title { margin: .25rem 0; font-weight: 740; color: var(--ink); }
    .method-copy { color: var(--muted); font-size: .88rem; line-height: 1.5; }
    div[data-baseweb="tab-list"] { gap: .4rem; }
    button[data-baseweb="tab"] {
        height: 2.8rem;
        padding: 0 1rem;
        border-radius: 10px;
    }
    div[data-baseweb="tab-highlight"] { background-color: var(--accent); }
    .stButton > button {
        border-color: #cbd8dd;
        background: white;
        color: var(--ink);
        border-radius: 10px;
    }
    .stButton > button:hover { border-color: var(--accent); color: var(--accent); }
    [data-testid="stChatMessage"] {
        background: white;
        border: 1px solid var(--line);
        border-radius: 14px;
    }
    @media (max-width: 700px) {
        .hero { padding: 1.55rem; border-radius: 15px; }
        .hero h1 { font-size: 2.4rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=60, show_spinner=False)
def cached_live() -> dict:
    return fetch_live_snapshot()


@st.cache_data(ttl=3600, show_spinner=False)
def cached_history(days: int) -> pd.DataFrame:
    return load_history(prepare_history(days=days))


def evidence_table(result: object) -> None:
    if isinstance(result, list):
        st.dataframe(pd.DataFrame(result), width="stretch", hide_index=True)
    elif isinstance(result, dict):
        st.json(result)
    else:
        st.write(result)


def format_snapshot_time(value: str) -> str:
    timestamp = pd.Timestamp(value)
    return timestamp.tz_convert("America/New_York").strftime("%-I:%M:%S %p ET")


def line_card(line: str, status: dict) -> None:
    alert_word = "alert" if status["active_alert_count"] == 1 else "alerts"
    st.markdown(
        f"""
        <div class="line-card" style="--route-color:{LINE_COLORS[line]}">
            <div class="line-name">{line} Line</div>
            <div class="line-value">{status["vehicle_count"]}</div>
            <div class="line-meta">vehicles visible · {status["active_alert_count"]} {alert_word}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def alert_card(alert: dict) -> None:
    routes = ", ".join(alert["routes"]) or "Network-wide / unspecified"
    st.markdown(
        f"""
        <div class="alert-card">
            <div class="alert-effect">{html.escape(alert.get("effect") or "NOTICE")}</div>
            <div class="alert-title">{html.escape(alert.get("header") or "Service alert")}</div>
            <div class="alert-routes">{html.escape(routes)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown("## T-Analyst")
    st.caption("An Auditable Agent for MBTA Transit Operations")
    st.markdown("---")
    st.markdown("#### Choose a time window")
    history_days = st.slider(
        "Recent days to compare",
        3,
        14,
        7,
        help="Today is left out because the day is not complete yet.",
    )
    st.markdown("#### What is included")
    st.markdown(
        """
        MBTA subway service  
        Live locations and notices  
        Recent train spacing
        """
    )
    st.markdown("#### Assistant status")
    if os.getenv("TRANSIT_LLM_API_KEY"):
        st.success("Ready to answer questions")
    else:
        st.info("Basic answers available")
    with st.expander("Data and model details"):
        st.caption(
            "Live data: MBTA V3 API\n\n"
            "History: MBTA LAMP\n\n"
            "Assistant: "
            + (
                "Parley GPT-5.5"
                if os.getenv("TRANSIT_LLM_API_KEY")
                else "deterministic fallback"
            )
        )

try:
    with st.spinner("Loading recent MBTA evidence…"):
        history = cached_history(history_days)
        live = cached_live()
except TransitDataError as exc:
    st.error(str(exc))
    st.stop()

snapshot_label = format_snapshot_time(live["fetched_at"])
service_dates = pd.to_datetime(
    history["service_date"].astype(str), format="%Y%m%d", errors="coerce"
)
window_label = (
    f"{service_dates.min():%b %-d}–{service_dates.max():%b %-d, %Y}"
    if service_dates.notna().any()
    else f"{history_days} recent days"
)
agent_label = "Parley GPT-5.5" if os.getenv("TRANSIT_LLM_API_KEY") else "Fallback mode"

st.markdown(
    f"""
    <div class="hero">
        <div class="eyebrow">Live and recent MBTA subway data</div>
        <h1>T-Analyst</h1>
        <p><strong>An Auditable Agent for MBTA Transit Operations.</strong><br>
        See how subway service is running, then ask a question in everyday language.</p>
        <div class="hero-badges">
            <span class="badge"><span class="live-dot"></span> Live snapshot · {snapshot_label}</span>
            <span class="badge">History · {window_label}</span>
            <span class="badge">Agent · {agent_label}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

overview_tab, ask_tab, methods_tab = st.tabs(
    ["Overview", "Ask a question", "About the data"]
)

with overview_tab:
    st.markdown('<div class="section-kicker">Live view</div>', unsafe_allow_html=True)
    st.subheader("How is the subway running?")
    st.markdown(
        '<p class="section-copy">Start with what is happening now, then compare it with recent service.</p>',
        unsafe_allow_html=True,
    )

    metrics = st.columns(4)
    metrics[0].metric(
        "Vehicles on the map",
        f"{len(live['vehicles']):,}",
        help="Vehicles currently reporting a location to the MBTA feed.",
    )
    metrics[1].metric(
        "Service notices",
        f"{len(live['alerts']):,}",
        help="Current notices returned by the MBTA alerts feed.",
    )
    metrics[2].metric(
        "Stops analyzed",
        f"{len(history):,}",
        help="Completed trip-stop records in the selected historical window.",
    )
    metrics[3].metric("Days compared", f"{history_days}")

    st.markdown("#### A quick look at each line")
    columns = st.columns(4)
    for column, line in zip(columns, LINE_GROUPS):
        status = live_line_status(live, line)
        with column:
            line_card(line, status)

    st.markdown("#### Where trains are reporting from")
    vehicles = pd.DataFrame(live["vehicles"]).dropna(subset=["latitude", "longitude"])
    if not vehicles.empty:
        figure = px.scatter_map(
            vehicles,
            lat="latitude",
            lon="longitude",
            color="route_id",
            color_discrete_map=LINE_COLORS,
            hover_name="vehicle_id",
            hover_data={
                "route_id": True,
                "status": True,
                "updated_at": True,
                "latitude": False,
                "longitude": False,
            },
            zoom=10,
            height=510,
        )
        figure.update_traces(marker={"size": 12, "opacity": 0.88})
        figure.update_layout(
            map_style="carto-positron",
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.01,
                xanchor="left",
                x=0,
                title=None,
            ),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(figure, config={"displayModeBar": False})

    reliability = pd.DataFrame(network_reliability(history))
    reliability["gap_percent"] = reliability["gap_rate"] * 100
    reliability = reliability.sort_values("gap_percent")
    worst = reliability.iloc[-1]
    st.markdown(
        f"""
        <div class="insight">
            <strong>One thing to notice:</strong> {html.escape(str(worst["route_id"]))}
            had the highest share of unusually long spaces between trains in this window:
            <strong>{worst["gap_percent"]:.1f}%</strong>, across
            {int(worst["observations"]):,} usable observations.
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.65, 1], gap="large")
    with left:
        st.markdown("#### How often train spacing was unusually long")
        st.caption(
            "Share of completed train intervals that were more than 1.5× the scheduled interval"
        )
        bar = go.Figure(
            go.Bar(
                x=reliability["gap_percent"],
                y=reliability["route_id"],
                orientation="h",
                marker_color=[
                    LINE_COLORS.get(route, "#547582")
                    for route in reliability["route_id"]
                ],
                text=[f"{value:.1f}%" for value in reliability["gap_percent"]],
                textposition="outside",
                hovertemplate=(
                    "<b>%{y}</b><br>Unusually long intervals: %{x:.1f}%"
                    "<br><extra></extra>"
                ),
            )
        )
        bar.update_layout(
            height=385,
            margin=dict(l=10, r=45, t=10, b=35),
            xaxis=dict(
                title="Share of usable train intervals",
                ticksuffix="%",
                gridcolor="#e8edef",
            ),
            yaxis=dict(title=None),
            plot_bgcolor="white",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )
        st.plotly_chart(bar, config={"displayModeBar": False})
        with st.expander("See the detailed numbers"):
            display = reliability.drop(columns=["gap_percent"]).copy()
            display["gap_rate"] = display["gap_rate"].map(lambda value: f"{value:.1%}")
            display["bunching_rate"] = display["bunching_rate"].map(
                lambda value: f"{value:.1%}"
            )
            st.dataframe(
                display,
                width="stretch",
                hide_index=True,
                column_config={
                    "route_id": "Route",
                    "observations": st.column_config.NumberColumn(
                        "Usable intervals", format="%d"
                    ),
                    "median_headway_ratio": "Typical interval ÷ schedule",
                    "p90_headway_ratio": "Long-end interval ÷ schedule",
                    "gap_rate": "Unusually long",
                    "bunching_rate": "Very close together",
                    "median_travel_time_excess_seconds": "Typical travel difference (sec)",
                },
            )
    with right:
        st.markdown("#### Current service notices")
        st.caption(f"Last checked at {snapshot_label}")
        if live["alerts"]:
            for alert in live["alerts"][:6]:
                alert_card(alert)
        else:
            st.markdown(
                '<div class="empty-state">No subway alerts in this snapshot.</div>',
                unsafe_allow_html=True,
            )

    st.caption(
        "About these numbers: live arrival estimates can change. The spacing chart "
        "uses completed train movements, not future predictions."
    )

with ask_tab:
    st.markdown('<div class="section-kicker">Ask in your own words</div>', unsafe_allow_html=True)
    st.subheader("What would you like to know?")
    st.markdown(
        '<p class="section-copy">You do not need to know GTFS, SQL, or transit data terminology. '
        "Choose an example or type a question below.</p>",
        unsafe_allow_html=True,
    )
    examples = [
        "Which line had the most uneven train spacing recently?",
        "How has the Red Line been running?",
        "What is happening on the Orange Line right now?",
        "Which current notices should I pay attention to?",
        "How do you decide that a gap is unusually long?",
    ]
    st.markdown("**Suggested questions**")
    example_columns = st.columns(3)
    selected = None
    for index, example in enumerate(examples):
        if example_columns[index % 3].button(
            example,
            key=f"example-{index}",
            width="stretch",
        ):
            selected = example
    question = st.chat_input(
        "For example: How has the Red Line been running?"
    ) or selected
    if question:
        st.session_state["last_question"] = question
        with st.chat_message("user"):
            st.write(question)
        analyst = TransitAnalyst(history=history, live_snapshot=live)
        try:
            with st.spinner("Planning, querying, and checking evidence…"):
                result = analyst.ask(question)
        except Exception as exc:
            st.error(f"Analysis failed safely: {exc}")
        else:
            st.session_state["last_result"] = result
            with st.chat_message("assistant"):
                st.markdown(result.answer)
                st.caption("Answer checked against the data used in this session")
            with st.expander("See how this answer was made"):
                st.markdown("**How your question was understood**")
                st.write(result.plan.interpreted_question)
                for item in result.evidence:
                    st.markdown(
                        f"**[{item['evidence_id']}] {item['source']}**"
                    )
                    st.caption(item["reason"])
                    with st.expander(f"Technical details: {item['tool']}"):
                        st.markdown("**Inputs**")
                        st.code(str(item["arguments"]), language="python")
                        st.markdown("**Data returned**")
                        evidence_table(item["result"])
    else:
        st.markdown(
            """
            <div class="empty-state">
                <strong>Start with a question.</strong><br>
                Pick one of the examples above, or ask about the line you use.
            </div>
            """,
            unsafe_allow_html=True,
        )

with methods_tab:
    st.markdown('<div class="section-kicker">What is behind the answer</div>', unsafe_allow_html=True)
    st.subheader("Simple on the surface, checkable underneath")
    st.markdown(
        '<p class="section-copy">The assistant helps understand the question, '
        "but the displayed numbers are calculated directly from MBTA data.</p>",
        unsafe_allow_html=True,
    )
    method_columns = st.columns(3)
    method_content = [
        (
            "01",
            "Understand",
            "The assistant identifies the line, time period, and type of information you need.",
        ),
        (
            "02",
            "Look it up",
            "A small set of read-only tools calculates the answer from MBTA V3 and LAMP data.",
        ),
        (
            "03",
            "Check",
            "The answer must point back to data from the same session, or the app falls back safely.",
        ),
    ]
    for column, (number, title, copy) in zip(method_columns, method_content):
        with column:
            st.markdown(
                f"""
                <div class="method-card">
                    <div class="method-number">{number}</div>
                    <div class="method-title">{title}</div>
                    <div class="method-copy">{copy}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("#### What the measures mean")
    definitions = metric_definition()
    definition_columns = st.columns(2)
    for index, (metric, definition) in enumerate(definitions.items()):
        definition_columns[index % 2].markdown(
            f"**{metric.replace('_', ' ').title()}**  \n{definition}"
        )

    st.markdown("#### What to keep in mind")
    st.warning(
        "Seven recent service days are a demonstration window, not a long-run trend. "
        "Results do not control for incidents, demand, construction, or schedule changes."
    )
    st.markdown(
        """
        **Audit guarantees**
        - No arbitrary model-generated SQL.
        - Tool names and arguments are schema-validated.
        - Numeric answers must cite evidence returned in the same run.
        - API timestamps and sample counts remain visible.
        """
    )
