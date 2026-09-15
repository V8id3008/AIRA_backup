"""Bounded validation workflows for A.I.R.A."""

from __future__ import annotations

from pathlib import Path

from agents.debug_agent import CheckResult, DebugAgent


class TestingAgent:
    """Run safe, bounded checks and summarize validation status."""

    def __init__(self, project_root: str | Path | None = None, timeout: int = 30):
        self.debugger = DebugAgent(project_root=project_root, timeout=timeout)

    def run_compile_check(self) -> CheckResult:
        return self.debugger.run_compile_check()

    def run_tests(self) -> CheckResult:
        return self.debugger.run_tests()

    def verify(self) -> list[CheckResult]:
        return [self.run_compile_check(), self.run_tests()]

    def report(self) -> str:
        results = self.verify()
        lines = ["A.I.R.A. Test Report"]
        for result in results:
            status = "PASS" if result.passed is True else "FAIL" if result.passed is False else "UNAVAILABLE"
            lines.append(f"[{status}] {result.name}: {result.output}")
        return "\n".join(lines)
