"""Read-only repository analysis for future coding workflows."""

from __future__ import annotations

from pathlib import Path


class CodingAgent:
    """Inspect code and prepare a change plan without editing files."""

    def __init__(self, project_root: str | Path | None = None):
        self.project_root = Path(project_root or Path(__file__).resolve().parents[1]).resolve()

    def list_source_files(self) -> list[str]:
        return sorted(
            str(path.relative_to(self.project_root))
            for path in self.project_root.rglob("*.py")
            if ".git" not in path.parts and "venv" not in path.parts and "__pycache__" not in path.parts
        )

    def read_file(self, relative_path: str, max_chars: int = 12000) -> str:
        path = (self.project_root / relative_path).resolve()
        if self.project_root not in path.parents and path != self.project_root:
            raise ValueError("Path is outside the project root")
        if path.suffix != ".py":
            raise ValueError("CodingAgent only reads Python source files")
        return path.read_text(encoding="utf-8")[:max_chars]

    def propose(self, request: str) -> str:
        files = self.list_source_files()
        return (
            f"Coding request: {request.strip()}\n"
            f"Repository Python files: {len(files)}\n"
            "Next step: inspect the relevant files, propose a minimal diff, then run tests."
        )
