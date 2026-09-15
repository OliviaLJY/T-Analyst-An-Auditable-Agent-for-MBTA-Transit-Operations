"""Agent orchestration for T-Analyst: An Auditable Agent for MBTA Transit Operations."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Callable

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from transit_data import (
    live_line_status,
    metric_definition,
    network_reliability,
    station_headways,
)

load_dotenv()

PARLEY_BASE_URL = "https://parley.api.mit.edu/v1"
TOOL_ARGUMENTS = {
    "network_reliability": {"line"},
    "station_headways": {"station", "line"},
    "live_line_status": {"line"},
    "metric_definition": {"metric"},
}
VALID_LINES = {"Red", "Orange", "Blue", "Green"}


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    reason: str


class AgentPlan(BaseModel):
    interpreted_question: str
    calls: list[ToolCall] = Field(min_length=1, max_length=3)


@dataclass
class AgentResult:
    answer: str
    plan: AgentPlan
    evidence: list[dict[str, Any]]
    model: str
    used_llm: bool
    citation_valid: bool
    fallback_triggered: bool
    fallback_reason: str | None


class TransitAnalyst:
    """LLM plans and explains; deterministic Python tools produce every number."""

    def __init__(
        self,
        history: pd.DataFrame,
        live_snapshot: dict[str, Any],
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.history = history
        self.live_snapshot = live_snapshot
        self.api_key = api_key or os.getenv("TRANSIT_LLM_API_KEY")
        self.client = (
            OpenAI(api_key=self.api_key, base_url=PARLEY_BASE_URL)
            if self.api_key
            else None
        )
        self.model = model or os.getenv("TRANSIT_LLM_MODEL") or ""
        self.tools: dict[str, Callable[..., Any]] = {
            "network_reliability": self._network_reliability,
            "station_headways": self._station_headways,
            "live_line_status": self._live_line_status,
            "metric_definition": metric_definition,
        }

    def _resolve_model(self) -> str:
        if self.model:
            return self.model
        if not self.client:
            return "deterministic-fallback"
        available = [item.id for item in self.client.models.list().data]
        matches = [model for model in available if "gpt-5.5" in model.lower()]
        if not matches:
            raise RuntimeError(
                "GPT-5.5 was not returned by Parley /models. "
                f"Available GPT models: {[m for m in available if 'gpt' in m.lower()]}"
            )
        self.model = matches[0]
        return self.model

    def _network_reliability(self, line: str | None = None) -> Any:
        return network_reliability(self.history, line=line)

    def _station_headways(self, station: str, line: str | None = None) -> Any:
        return station_headways(self.history, station=station, line=line)

    def _live_line_status(self, line: str | None = None) -> Any:
        return live_line_status(self.live_snapshot, line=line)

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ValueError("Planner did not return a JSON object.")
        return json.loads(match.group(0))

    def _fallback_plan(self, question: str) -> AgentPlan:
        lower = question.lower()
        aliases = {
            "red": "Red",
            "红线": "Red",
            "orange": "Orange",
            "橙线": "Orange",
            "blue": "Blue",
            "蓝线": "Blue",
            "green": "Green",
            "绿线": "Green",
        }
        line = next(
            (
                value
                for key, value in aliases.items()
                if (
                    key in lower
                    if not key.isascii()
                    else re.search(rf"\b{re.escape(key)}\b", lower)
                )
            ),
            None,
        )
        station_aliases = {
            "harvard": "Harvard",
            "kendall/mit": "Kendall/MIT",
            "kendall": "Kendall/MIT",
            "state": "State",
        }
        station = next(
            (value for key, value in station_aliases.items() if key in lower), None
        )
        asks_live = any(
            token in lower
            for token in (
                "now",
                "live",
                "current",
                "alert",
                "notice",
                "happening",
                "现在",
                "实时",
                "警报",
                "通知",
            )
        )
        asks_method = any(
            token in lower
            for token in (
                "define",
                "metric",
                "mean",
                "decide",
                "difference",
                "calculate",
                "calculated",
                "how do you",
                "怎么算",
                "定义",
                "指标",
            )
        )
        asks_history = any(
            token in lower
            for token in (
                "recent",
                "reliability",
                "headway",
                "spacing",
                "历史",
                "最近",
            )
        )
        if station:
            calls = [
                ToolCall(
                    name="station_headways",
                    arguments={"station": station, "line": line},
                    reason="The question asks about realized headways at a station.",
                )
            ]
        elif asks_live and asks_history:
            calls = [
                ToolCall(
                    name="live_line_status",
                    arguments={"line": line},
                    reason="Use the current service snapshot.",
                ),
                ToolCall(
                    name="network_reliability",
                    arguments={"line": line},
                    reason="Compare with recently realized operations.",
                ),
            ]
        elif asks_live:
            calls = [
                ToolCall(
                    name="live_line_status",
                    arguments={"line": line},
                    reason="The question asks about current service.",
                )
            ]
        elif asks_method:
            calls = [
                ToolCall(
                    name="metric_definition",
                    arguments={},
                    reason="The question asks how metrics are defined.",
                )
            ]
        else:
            calls = [
                ToolCall(
                    name="network_reliability",
                    arguments={"line": line},
                    reason="Use realized historical operations for a reliability question.",
                )
            ]
        return AgentPlan(interpreted_question=question, calls=calls)

    def _make_plan(self, question: str) -> AgentPlan:
        if not self.client:
            return self._fallback_plan(question)
        model = self._resolve_model()
        prompt = f"""You plan read-only MBTA subway analyses. Return JSON only.
Allowed tools:
- network_reliability(line?: Red|Orange|Blue|Green): historical line/route metrics
- station_headways(station: string, line?: Red|Orange|Blue|Green): realized station headways
- live_line_status(line?: Red|Orange|Blue|Green): current alerts, vehicles, predictions
- metric_definition(metric?: string): methodology
Choose the smallest sufficient plan:
- Use network_reliability for recent or historical route/line performance.
- Use station_headways for a historical question about a named station.
- Use live_line_status only when the user explicitly asks about now, current, live,
  alerts/notices, vehicles, or predictions.
- Use metric_definition only when the user asks what a metric means or how it is
  calculated. Do not add it merely because another tool returns that metric.
- If the user asks about multiple metric definitions, make one metric_definition
  call with no metric argument so it returns the full dictionary.
- Use two tools only when the question explicitly asks to compare live and recent
  service. Do not add tools for optional context.
Use 1-3 calls. Never invent another tool or parameter.
Schema:
{{"interpreted_question":"...", "calls":[{{"name":"...", "arguments":{{}}, "reason":"..."}}]}}
Question: {question}"""
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.choices[0].message.content or ""
        try:
            plan = AgentPlan.model_validate(self._extract_json(text))
        except (ValueError, json.JSONDecodeError, ValidationError):
            repair = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": text},
                    {
                        "role": "user",
                        "content": "Repair the response. Return one valid JSON object only.",
                    },
                ],
            )
            plan = AgentPlan.model_validate(
                self._extract_json(repair.choices[0].message.content or "")
            )
        self._validate_calls(plan)
        return plan

    def _validate_calls(self, plan: AgentPlan) -> None:
        for call in plan.calls:
            if call.name not in self.tools:
                raise ValueError(f"Planner selected unsupported tool: {call.name}")
            extras = set(call.arguments).difference(TOOL_ARGUMENTS[call.name])
            if extras:
                raise ValueError(f"Unsupported arguments for {call.name}: {sorted(extras)}")
            if call.name == "station_headways" and not call.arguments.get("station"):
                raise ValueError("station_headways requires a station.")
            line = call.arguments.get("line")
            if line is not None and line not in VALID_LINES:
                raise ValueError(f"Unsupported line: {line}")

    def _run_tools(self, plan: AgentPlan) -> list[dict[str, Any]]:
        self._validate_calls(plan)
        evidence = []
        for index, call in enumerate(plan.calls, start=1):
            result = self.tools[call.name](**call.arguments)
            evidence.append(
                {
                    "evidence_id": f"E{index}",
                    "tool": call.name,
                    "arguments": call.arguments,
                    "reason": call.reason,
                    "source": (
                        "MBTA V3 API"
                        if call.name == "live_line_status"
                        else (
                            "MBTA LAMP performance + MBTA V3 station metadata"
                            if call.name == "station_headways"
                            else "MBTA LAMP daily subway performance data"
                        )
                    ),
                    "result": result,
                }
            )
        return evidence

    def _fallback_answer(self, evidence: list[dict[str, Any]]) -> str:
        parts = ["Parley is unavailable, so this is a deterministic evidence summary."]
        for item in evidence:
            result = item["result"]
            if isinstance(result, list) and result:
                worst = result[0]
                parts.append(
                    f"[{item['evidence_id']}] {worst.get('route_id', 'Result')}: "
                    f"gap rate {worst.get('gap_rate', 'n/a')}, based on "
                    f"{worst.get('observations', 'n/a')} observations."
                )
            elif isinstance(result, dict):
                parts.append(
                    f"[{item['evidence_id']}] "
                    + json.dumps(result, ensure_ascii=False, default=str)[:700]
                )
        return "\n\n".join(parts)

    @staticmethod
    def _citations_valid(answer: str, evidence: list[dict[str, Any]]) -> bool:
        valid_ids = {item["evidence_id"] for item in evidence}
        cited_ids = set(re.findall(r"\[(E\d+)\]", answer))
        return bool(cited_ids) and cited_ids.issubset(valid_ids)

    def _synthesize(
        self, question: str, plan: AgentPlan, evidence: list[dict[str, Any]]
    ) -> tuple[str, bool, str | None]:
        if not self.client:
            answer = self._fallback_answer(evidence)
            return answer, self._citations_valid(answer, evidence), "no_api_key"
        model = self._resolve_model()
        prompt = f"""Answer an MBTA transit analysis question from evidence only.
Lead with the finding, explain operational meaning, and state limitations.
Every numeric claim must cite an evidence ID exactly like [E1].
Do not call prediction gaps realized headways. Be concise.
Do not equate a realized headway with an individual rider's wait. Describe it as
train spacing unless passenger arrival or wait-time evidence is explicitly provided.
Question: {question}
Interpretation: {plan.interpreted_question}
Evidence: {json.dumps(evidence, ensure_ascii=False, default=str)}"""
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = response.choices[0].message.content or ""
        if not self._citations_valid(answer, evidence):
            fallback = self._fallback_answer(evidence)
            return (
                fallback,
                self._citations_valid(fallback, evidence),
                "citation_validation_failed",
            )
        return answer, True, None

    def ask(self, question: str) -> AgentResult:
        plan = self._make_plan(question)
        evidence = self._run_tools(plan)
        answer, citation_valid, fallback_reason = self._synthesize(
            question, plan, evidence
        )
        return AgentResult(
            answer=answer,
            plan=plan,
            evidence=evidence,
            model=self._resolve_model() if self.client else "deterministic-fallback",
            used_llm=bool(self.client),
            citation_valid=citation_valid,
            fallback_triggered=fallback_reason is not None,
            fallback_reason=fallback_reason,
        )
