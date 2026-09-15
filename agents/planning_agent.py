"""Deterministic task planning for A.I.R.A. agent workflows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanStep:
    number: int
    agent: str
    action: str


class PlanningAgent:
    """Create transparent, dependency-aware plans without side effects."""

    def create_plan(self, request: str) -> list[PlanStep]:
        text = request.lower().strip()
        steps = [PlanStep(1, "Planning Agent", "Clarify the goal, constraints, and expected outcome.")]

        if any(word in text for word in ("debug", "error", "broken", "test", "crash")):
            steps.extend([
                PlanStep(2, "Debugging Agent", "Run compile checks and bounded tests; collect failure output."),
                PlanStep(3, "Coding Agent", "Propose the smallest safe fix for the confirmed root cause."),
                PlanStep(4, "Testing Agent", "Re-run the affected checks and report regressions."),
            ])
        elif any(word in text for word in ("research", "search", "latest", "news", "find")):
            steps.extend([
                PlanStep(2, "Research Agent", "Search authoritative sources and collect evidence."),
                PlanStep(3, "Response Synthesis Agent", "Summarize findings with sources and uncertainty."),
                PlanStep(4, "Memory Agent", "Offer to save durable user-relevant findings."),
            ])
        elif any(word in text for word in ("code", "feature", "implement", "refactor", "python")):
            steps.extend([
                PlanStep(2, "Coding Agent", "Inspect the repository and identify the smallest implementation path."),
                PlanStep(3, "Testing Agent", "Add or update focused tests for the change."),
                PlanStep(4, "Code Review Agent", "Review the diff for correctness and regressions."),
            ])
        else:
            steps.extend([
                PlanStep(2, "Orchestrator Agent", "Select the specialist agents needed for this request."),
                PlanStep(3, "Response Synthesis Agent", "Combine validated agent results into a clear response."),
            ])

        return steps

    def format_plan(self, request: str) -> str:
        lines = ["A.I.R.A. Execution Plan", f"Goal: {request.strip() or 'No goal provided.'}", ""]
        lines.extend(f"{step.number}. {step.agent} — {step.action}" for step in self.create_plan(request))
        return "\n".join(lines)
