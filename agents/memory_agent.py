"""Long-term memory coordination for A.I.R.A."""

from __future__ import annotations

from dataclasses import dataclass

from memory.extractor import extract_memories
from memory.validator import MemoryValidator
from semantic_memory.memory_db import add_memory, get_all_memories
from semantic_memory.retriever import get_relevant_memories


@dataclass(frozen=True)
class MemoryWriteResult:
    text: str
    stored: bool
    memory_id: str | None
    updated: bool


class MemoryAgent:
    """Retrieve and persist validated memories with explicit write operations."""

    def __init__(self):
        self.validator = MemoryValidator()

    def recall(self, query: str, limit: int = 5) -> list[str]:
        if not isinstance(query, str) or not query.strip():
            return []
        return get_relevant_memories(query.strip(), limit=limit)

    def recall_report(self, query: str) -> str:
        memories = self.recall(query)
        if not memories:
            return "No relevant long-term memories found."
        return "Relevant long-term memories:\n" + "\n".join(f"- {memory}" for memory in memories)

    def extract_candidates(self, user_message: str, assistant_response: str) -> list[dict]:
        existing = [
            item.get("text", "")
            for memories in get_all_memories().values()
            for item in memories
            if item.get("text")
        ]
        return extract_memories(user_message, assistant_response, existing_memories=existing)

    def store(self, candidates: list[dict]) -> list[MemoryWriteResult]:
        """Persist validated candidates. Call only after an explicit write decision."""
        results = []
        for candidate in candidates:
            accepted, _ = self.validator.validate(candidate)
            if not accepted:
                results.append(MemoryWriteResult(candidate.get("text", ""), False, None, False))
                continue
            memory_id, updated = add_memory(**candidate)
            results.append(MemoryWriteResult(candidate["text"], memory_id is not None, memory_id, updated))
        return results
