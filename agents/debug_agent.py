"""Safe, read-only diagnostics for the A.I.R.A. project."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CheckResult:
    name: str
    passed: bool | None
    output: str


class DebugAgent:
    """Inspect and test the project without modifying files."""

    def __init__(self, project_root: str | Path | None = None, timeout: int = 30):
        self.project_root = Path(project_root or Path(__file__).resolve().parents[1]).resolve()
        self.timeout = timeout

    def inspect_project(self) -> str:
        files = sorted(
            str(path.relative_to(self.project_root))
            for path in self.project_root.rglob("*.py")
            if ".git" not in path.parts and "venv" not in path.parts and "__pycache__" not in path.parts
        )
        return "\n".join(files) if files else "No Python files found."

    def _run(self, name: str, args: list[str], timeout: int | None = None) -> CheckResult:
        try:
            completed = subprocess.run(
                args,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout or self.timeout,
                check=False,
            )
        except FileNotFoundError:
            return CheckResult(name, None, f"Command unavailable: {args[0]}")
        except subprocess.TimeoutExpired as exc:
            output = (exc.stdout or "") + (exc.stderr or "")
            return CheckResult(name, False, f"Timed out after {timeout or self.timeout}s.\n{output}")
        output = "\n".join(part for part in (completed.stdout, completed.stderr) if part).strip()
        return CheckResult(name, completed.returncode == 0, output or "No output.")

    def run_compile_check(self) -> CheckResult:
        targets = [
            "main.py",
            "backend",
            "memory",
            "orchestrator",
            "search",
            "semantic_memory",
            "agents",
        ]
        return self._run("Python compilation", [sys.executable, "-m", "compileall", "-q", *targets])

    def run_tests(self) -> CheckResult:
        target = "tests/test_agents.py"
        return self._run("Pytest agent checks", [sys.executable, "-m", "pytest", "-q", target], timeout=self.timeout)

    def diagnose(self, issue: str = "") -> str:
        results = [self.run_compile_check(), self.run_tests()]
        lines = ["A.I.R.A. Debug Agent", f"Project: {self.project_root}"]
        if issue.strip():
            lines.append(f"Reported issue: {issue.strip()}")
        lines.append("")
        for result in results:
            status = "PASS" if result.passed is True else "FAIL" if result.passed is False else "UNAVAILABLE"
            lines.extend([f"[{status}] {result.name}", result.output, ""])
        failed = [result.name for result in results if result.passed is False]
        if failed:
            lines.append("Next step: inspect the failure output above before applying a patch.")
        else:
            lines.append("No failing automated check was detected.")
        return "\n".join(lines)
