"""Controlled self-build orchestration for A.I.R.A."""

from __future__ import annotations

import argparse
from pathlib import Path

from agents.debug_agent import DebugAgent


class SelfBuildingAgent:
    """Inspect A.I.R.A. and plan its next build step without editing files."""

    AGENT_SEQUENCE = (
        "debug_agent",
        "planning_agent",
        "memory_agent",
        "research_agent",
        "coding_agent",
        "testing_agent",
        "code_review_agent",
        "documentation_agent",
        "system_agent",
        "security_agent",
        "multi_agent_coordinator",
    )

    def __init__(self, project_root: str | Path | None = None, timeout: int = 30):
        self.project_root = Path(project_root or Path(__file__).resolve().parents[1]).resolve()
        self.debugger = DebugAgent(self.project_root, timeout=timeout)

    def installed_agents(self) -> list[str]:
        agent_dir = self.project_root / "agents"
        return sorted(path.stem for path in agent_dir.glob("*_agent.py"))

    def next_agent(self) -> str | None:
        installed = set(self.installed_agents())
        return next((name for name in self.AGENT_SEQUENCE if name not in installed), None)

    def build_plan(self) -> str:
        installed = self.installed_agents()
        next_name = self.next_agent()
        lines = [
            "A.I.R.A. Self-Building Agent",
            f"Project: {self.project_root}",
            "",
            "Installed agents:",
            *[f"- {name}" for name in installed],
            "",
            f"Next agent: {next_name or 'All planned agents are present.'}",
            "Build policy: inspect -> plan -> approve -> edit -> test.",
            "Mode: read-only diagnostics; no files will be changed.",
        ]
        return "\n".join(lines)

    def run_build_cycle(self) -> str:
        compile_result = self.debugger.run_compile_check()
        test_result = self.debugger.run_tests()
        status = lambda result: "PASS" if result.passed is True else "FAIL" if result.passed is False else "UNAVAILABLE"
        return "\n".join([
            self.build_plan(),
            "",
            f"Python compilation: {status(compile_result)}",
            f"Agent tests: {status(test_result)}",
            "",
            "Next action: review the plan before enabling any write operation.",
        ])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run A.I.R.A.'s controlled self-building check.")
    parser.add_argument("--plan-only", action="store_true", help="Show the build plan without running checks.")
    args = parser.parse_args()
    agent = SelfBuildingAgent()
    print(agent.build_plan() if args.plan_only else agent.run_build_cycle())


if __name__ == "__main__":
    main()
